"""
Multi-API HTTP proxy server for MCP OAuth Bridge

This module provides a proxy server that:
- Accepts requests from OpenAI and Anthropic APIs
- Forwards them to MCP servers with OAuth token injection
- Handles token refresh automatically
- Provides approval management
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs
import uuid

from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import uvicorn

from .config import Config
from .oauth import OAuthHandler
from .tokens import TokenManager
from .approvals import ApprovalManager
from .adapters.openai import OpenAIAdapter
from .adapters.anthropic import AnthropicAdapter

logger = logging.getLogger(__name__)


class ProxyServer:
    """Multi-API HTTP proxy server for MCP OAuth Bridge"""
    
    def __init__(self, config: Config):
        self.config = config
        self.oauth_handler = OAuthHandler(config)
        self.token_manager = TokenManager(config)
        self.approval_manager = ApprovalManager(config)
        self.openai_adapter = OpenAIAdapter()
        self.anthropic_adapter = AnthropicAdapter()
        
        # Create FastAPI app
        self.app = FastAPI(title="MCP OAuth Bridge", version="0.1.0")
        
        # Setup templates
        self.templates = Jinja2Templates(directory="templates")
        
        # Setup routes
        self._setup_routes()
        
        # HTTP client for forwarding requests
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    def _setup_routes(self):
        """Setup all HTTP routes"""
        
        # Health check
        @self.app.get("/")
        async def health_check():
            return {"status": "ok", "message": "MCP OAuth Bridge is running"}
        
        # MCP server proxy routes
        @self.app.api_route("/mcp/{server_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def proxy_mcp_request(server_name: str, path: str, request: Request):
            return await self._handle_mcp_request(server_name, path, request)
        
        # OpenAI-specific routes
        @self.app.post("/openai/responses")
        async def openai_responses(request: Request):
            return await self._handle_openai_request(request)
        
        # Anthropic-specific routes  
        @self.app.post("/anthropic/messages")
        async def anthropic_messages(request: Request):
            return await self._handle_anthropic_request(request)
        
        # Approval UI routes
        @self.app.get("/approvals", response_class=HTMLResponse)
        async def approval_ui(request: Request):
            pending_approvals = await self.approval_manager.get_pending_approvals()
            return self.templates.TemplateResponse(
                "approvals.html", 
                {"request": request, "approvals": pending_approvals}
            )
        
        @self.app.post("/approvals/{approval_id}/approve")
        async def approve_request(approval_id: str):
            success = await self.approval_manager.approve_request(approval_id)
            if success:
                return {"status": "approved"}
            raise HTTPException(status_code=404, detail="Approval not found")
        
        @self.app.post("/approvals/{approval_id}/deny")
        async def deny_request(approval_id: str):
            success = await self.approval_manager.deny_request(approval_id)
            if success:
                return {"status": "denied"}
            raise HTTPException(status_code=404, detail="Approval not found")
        
        # Configuration routes
        @self.app.get("/config/servers")
        async def list_servers():
            return {"servers": list(self.config.servers.keys())}
        
        @self.app.get("/config/servers/{server_name}")
        async def get_server_config(server_name: str):
            server = self.config.get_server(server_name)
            if not server:
                raise HTTPException(status_code=404, detail="Server not found")
            return {"server": server}
    
    async def _handle_mcp_request(self, server_name: str, path: str, request: Request) -> Response:
        """Handle direct MCP server requests with OAuth token injection"""
        try:
            # Get server configuration
            server = self.config.get_server(server_name)
            if not server:
                raise HTTPException(status_code=404, detail=f"Server '{server_name}' not configured")
            
            # Get OAuth token
            token = self.token_manager.get_token(server_name)
            if not token:
                raise HTTPException(status_code=401, detail=f"No valid OAuth token for server '{server_name}'")
            
            # Prepare target URL
            target_url = f"{server['url'].rstrip('/')}/{path.lstrip('/')}"
            
            # Get request data
            body = await request.body()
            headers = dict(request.headers)
            
            # Remove host and content-length headers
            headers.pop('host', None)
            headers.pop('content-length', None)
            
            # Add OAuth token
            headers['Authorization'] = f"Bearer {token['access_token']}"
            
            # Forward request
            response = await self.http_client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                params=dict(request.query_params)
            )
            
            # Handle token refresh if needed
            if response.status_code == 401:
                logger.info(f"Token expired for {server_name}, attempting refresh")
                refreshed = await self._refresh_token(server_name)
                if refreshed:
                    # Retry with new token
                    token = self.token_manager.get_token(server_name)
                    headers['Authorization'] = f"Bearer {token['access_token']}"
                    response = await self.http_client.request(
                        method=request.method,
                        url=target_url,
                        content=body,
                        headers=headers,
                        params=dict(request.query_params)
                    )
            
            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except Exception as e:
            logger.error(f"Error handling MCP request for {server_name}/{path}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _handle_openai_request(self, request: Request) -> Response:
        """Handle OpenAI Responses API requests"""
        try:
            body = await request.json()
            result = await self.openai_adapter.handle_request(body)
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"Error handling OpenAI request: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _handle_anthropic_request(self, request: Request) -> Response:
        """Handle Anthropic Messages API requests"""
        try:
            body = await request.json()
            result = await self.anthropic_adapter.handle_request(body)
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"Error handling Anthropic request: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _refresh_token(self, server_name: str) -> bool:
        """Refresh OAuth token for a server"""
        try:
            server = self.config.get_server(server_name)
            if not server:
                return False
            
            # Get current token
            current_token = self.token_manager.get_token(server_name)
            if not current_token or not current_token.get('refresh_token'):
                return False
            
            # Refresh token
            new_token = await self.oauth_handler.refresh_token(
                server['oauth_config'], 
                current_token['refresh_token']
            )
            
            if new_token:
                # Store new token
                self.token_manager.store_token(server_name, new_token)
                logger.info(f"Successfully refreshed token for {server_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error refreshing token for {server_name}: {e}")
            return False
    
    async def start(self, host: str = "localhost", port: int = 3000):
        """Start the proxy server"""
        logger.info(f"🚀 MCP OAuth Bridge starting on http://{host}:{port}")
        logger.info(f"📋 Approval UI available at http://{host}:{port}/approvals")
        
        # List configured servers
        servers = list(self.config.servers.keys())
        if servers:
            logger.info(f"🔧 Configured servers: {', '.join(servers)}")
        else:
            logger.warning("⚠️ No servers configured. Use 'mcp-oauth-bridge add' to add servers.")
        
        logger.info("🔌 Supporting OpenAI Responses API and Anthropic Messages API")
        
        # Start server
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self):
        """Stop the proxy server and cleanup"""
        await self.http_client.aclose()
        logger.info("🛑 MCP OAuth Bridge stopped")


def create_proxy_server(config_path: Optional[str] = None) -> ProxyServer:
    """Create and configure a proxy server instance"""
    config = Config(config_path)
    return ProxyServer(config)


async def run_proxy_server(config_path: Optional[str] = None, host: str = "localhost", port: int = 3000):
    """Run the proxy server (convenience function)"""
    proxy = create_proxy_server(config_path)
    try:
        await proxy.start(host, port)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await proxy.stop()


if __name__ == "__main__":
    # Run directly for development
    asyncio.run(run_proxy_server()) 