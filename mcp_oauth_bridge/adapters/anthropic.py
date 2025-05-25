"""
Anthropic API adapter for MCP OAuth Bridge

Handles translation between Anthropic Messages API format and MCP protocol.
Supports Anthropic's MCP server integration patterns.
"""

from typing import Dict, Any, Optional, List
import httpx
import json
from urllib.parse import urljoin


class AnthropicAdapter:
    """Adapter for Anthropic Messages API format"""
    
    def __init__(self, timeout: int = 30) -> None:
        """Initialize Anthropic adapter
        
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
    
    def detect_anthropic_request(self, request_data: Dict[str, Any]) -> bool:
        """Detect if this is an Anthropic-style request
        
        Args:
            request_data: Request data to analyze
            
        Returns:
            True if this looks like an Anthropic request
        """
        # Check for Anthropic-specific patterns
        if 'mcp_servers' in request_data:
            return True
        
        # Check for other Anthropic-specific fields
        anthropic_fields = [
            'messages', 'system', 'max_tokens', 'stop_sequences',
            'temperature', 'top_p', 'top_k'
        ]
        
        # Must have messages field for Anthropic
        if 'messages' not in request_data:
            return False
        
        return any(field in request_data for field in anthropic_fields)
    
    def extract_mcp_server_info(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract MCP server information from Anthropic request
        
        Args:
            request_data: Anthropic request data
            
        Returns:
            List of MCP server configurations
        """
        servers = []
        mcp_servers = request_data.get('mcp_servers', [])
        
        for server in mcp_servers:
            if isinstance(server, dict):
                server_info = {
                    'name': server.get('name', 'unknown'),
                    'url': server.get('url'),
                    'type': server.get('type', 'url'),
                    'require_approval': 'always',  # Default for Anthropic
                }
                if server_info['url']:
                    servers.append(server_info)
        
        return servers
    
    def extract_user_message(self, request_data: Dict[str, Any]) -> str:
        """Extract user message from Anthropic messages format
        
        Args:
            request_data: Anthropic request data
            
        Returns:
            Combined user message text
        """
        messages = request_data.get('messages', [])
        user_messages = []
        
        for message in messages:
            if isinstance(message, dict) and message.get('role') == 'user':
                content = message.get('content', '')
                if isinstance(content, list):
                    # Handle content blocks
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            text_parts.append(block.get('text', ''))
                    content = ' '.join(text_parts)
                user_messages.append(str(content))
        
        return ' '.join(user_messages)
    
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
    
    def convert_anthropic_to_mcp(self, anthropic_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert Anthropic request to MCP format
        
        Args:
            anthropic_request: Anthropic Messages API request
            
        Returns:
            List of MCP requests to send to servers
        """
        mcp_requests = []
        
        # Extract user input from messages
        user_input = self.extract_user_message(anthropic_request)
        if not user_input:
            return mcp_requests
        
        # Get MCP server configurations
        servers = self.extract_mcp_server_info(anthropic_request)
        
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
                            'model': anthropic_request.get('model'),
                            'system': anthropic_request.get('system'),
                            'max_tokens': anthropic_request.get('max_tokens'),
                            'temperature': anthropic_request.get('temperature'),
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
    
    def convert_mcp_to_anthropic(
        self, 
        mcp_responses: List[Dict[str, Any]], 
        original_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert MCP responses back to Anthropic format
        
        Args:
            mcp_responses: List of MCP server responses
            original_request: Original Anthropic request
            
        Returns:
            Anthropic Messages API response
        """
        # Combine all MCP responses into a single assistant message
        content_parts = []
        
        for mcp_response in mcp_responses:
            if 'error' in mcp_response:
                error_msg = mcp_response['error'].get('message', 'Unknown error')
                content_parts.append(f"Error: {error_msg}")
            else:
                result = mcp_response.get('result', {})
                content = result.get('content', str(result))
                content_parts.append(content)
        
        # Build Anthropic response format
        response_content = '\n\n'.join(content_parts) if content_parts else "No valid responses from MCP servers"
        
        response = {
            'id': f'msg_{hash(str(original_request))}',
            'type': 'message',
            'role': 'assistant',
            'content': [
                {
                    'type': 'text',
                    'text': response_content
                }
            ],
            'model': original_request.get('model', 'claude-3-sonnet-20240229'),
            'stop_reason': 'end_turn',
            'stop_sequence': None,
        }
        
        # Add usage information
        response['usage'] = {
            'input_tokens': self._estimate_tokens(self.extract_user_message(original_request)),
            'output_tokens': self._estimate_tokens(response_content),
        }
        
        return response
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation for usage stats
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Very rough estimation: ~4 characters per token
        return max(1, len(text) // 4)
    
    def build_approval_request(self, mcp_request: Dict[str, Any], server_name: str) -> Dict[str, Any]:
        """Build approval request for Anthropic format
        
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