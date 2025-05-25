"""
OpenAI API adapter for MCP OAuth Bridge

Handles translation between OpenAI Responses API format and MCP protocol.
Supports OpenAI's MCP tool integration patterns.
"""

from typing import Dict, Any, Optional, List
import httpx
import json
from urllib.parse import urljoin


class OpenAIAdapter:
    """Adapter for OpenAI Responses API format"""
    
    def __init__(self, timeout: int = 30) -> None:
        """Initialize OpenAI adapter
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.client = httpx.AsyncClient()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()
    
    def detect_openai_request(self, request_data: Dict[str, Any]) -> bool:
        """Detect if this is an OpenAI-style request
        
        Args:
            request_data: Request data to analyze
            
        Returns:
            True if this looks like an OpenAI request
        """
        # Check for OpenAI-specific patterns
        if 'tools' in request_data:
            tools = request_data['tools']
            if isinstance(tools, list) and len(tools) > 0:
                # Check for OpenAI MCP tool format
                for tool in tools:
                    if isinstance(tool, dict) and tool.get('type') == 'mcp':
                        return True
        
        # Check for other OpenAI-specific fields
        openai_fields = [
            'model', 'input', 'response_format', 'tool_choice',
            'require_approval', 'server_label', 'server_url'
        ]
        
        return any(field in request_data for field in openai_fields)
    
    def extract_mcp_server_info(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract MCP server information from OpenAI request
        
        Args:
            request_data: OpenAI request data
            
        Returns:
            List of MCP server configurations
        """
        servers = []
        tools = request_data.get('tools', [])
        
        for tool in tools:
            if isinstance(tool, dict) and tool.get('type') == 'mcp':
                server_info = {
                    'name': tool.get('server_label', 'unknown'),
                    'url': tool.get('server_url'),
                    'require_approval': tool.get('require_approval', 'always'),
                }
                if server_info['url']:
                    servers.append(server_info)
        
        return servers
    
    async def forward_to_mcp_server(
        self, 
        server_url: str, 
        mcp_request: Dict[str, Any], 
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Forward request to MCP server
        
        Args:
            server_url: MCP server URL
            mcp_request: MCP-formatted request
            auth_token: OAuth token for authorization
            
        Returns:
            MCP server response
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        try:
            response = await self.client.post(
                server_url,
                json=mcp_request,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # Token might be expired, let the proxy handle refresh
                raise ValueError("Authentication failed - token may need refresh")
            raise
        except Exception as e:
            raise ValueError(f"MCP server request failed: {e}")
    
    def convert_openai_to_mcp(self, openai_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert OpenAI request to MCP format
        
        Args:
            openai_request: OpenAI Responses API request
            
        Returns:
            List of MCP requests to send to servers
        """
        mcp_requests = []
        
        # Extract input/prompt from OpenAI request
        user_input = openai_request.get('input', '')
        if not user_input:
            return mcp_requests
        
        # Get MCP server configurations
        servers = self.extract_mcp_server_info(openai_request)
        
        for server in servers:
            # Build MCP request format
            mcp_request = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/call',
                'params': {
                    'name': 'process_request',  # Generic tool name
                    'arguments': {
                        'user_input': user_input,
                        'context': {
                            'model': openai_request.get('model'),
                            'require_approval': server.get('require_approval', 'always'),
                        }
                    }
                }
            }
            
            mcp_requests.append({
                'server_name': server['name'],
                'server_url': server['url'],
                'request': mcp_request,
                'require_approval': server.get('require_approval', 'always')
            })
        
        return mcp_requests
    
    def convert_mcp_to_openai(
        self, 
        mcp_responses: List[Dict[str, Any]], 
        original_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert MCP responses back to OpenAI format
        
        Args:
            mcp_responses: List of MCP server responses
            original_request: Original OpenAI request
            
        Returns:
            OpenAI Responses API response
        """
        # Build OpenAI response format
        response = {
            'id': f'resp_{hash(str(original_request))}',
            'object': 'response',
            'created': int(__import__('time').time()),
            'model': original_request.get('model', 'gpt-4'),
        }
        
        # Process MCP responses into choices
        choices = []
        for i, mcp_response in enumerate(mcp_responses):
            if 'error' in mcp_response:
                # Handle error responses
                choice = {
                    'index': i,
                    'finish_reason': 'error',
                    'message': {
                        'role': 'assistant',
                        'content': f"Error: {mcp_response['error'].get('message', 'Unknown error')}"
                    }
                }
            else:
                # Handle successful responses
                result = mcp_response.get('result', {})
                content = result.get('content', str(result))
                
                choice = {
                    'index': i,
                    'finish_reason': 'stop',
                    'message': {
                        'role': 'assistant',
                        'content': content
                    }
                }
                
                # Add tool calls if present
                if 'tool_calls' in result:
                    choice['message']['tool_calls'] = result['tool_calls']
            
            choices.append(choice)
        
        response['choices'] = choices if choices else [{
            'index': 0,
            'finish_reason': 'stop',
            'message': {
                'role': 'assistant',
                'content': 'No valid responses from MCP servers'
            }
        }]
        
        # Add usage information
        response['usage'] = {
            'prompt_tokens': len(original_request.get('input', '').split()),
            'completion_tokens': sum(
                len(choice['message']['content'].split()) 
                for choice in response['choices']
            ),
            'total_tokens': 0
        }
        response['usage']['total_tokens'] = (
            response['usage']['prompt_tokens'] + 
            response['usage']['completion_tokens']
        )
        
        return response
    
    def build_approval_request(self, mcp_request: Dict[str, Any], server_name: str) -> Dict[str, Any]:
        """Build approval request for OpenAI format
        
        Args:
            mcp_request: MCP request that needs approval
            server_name: Name of the server
            
        Returns:
            Approval request data
        """
        return {
            'id': f'approval_{hash(str(mcp_request))}',
            'type': 'tool_approval',
            'server_name': server_name,
            'tool_name': mcp_request['params'].get('name', 'unknown'),
            'arguments': mcp_request['params'].get('arguments', {}),
            'description': f"Tool call to {server_name}: {mcp_request['params'].get('name')}",
            'timestamp': __import__('datetime').datetime.now().isoformat(),
        } 