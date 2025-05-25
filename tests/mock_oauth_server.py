#!/usr/bin/env python3
"""
Mock OAuth MCP Server for testing MCP OAuth Bridge

This server implements:
- OAuth 2.1 with PKCE flows
- MCP protocol endpoints
- Dynamic client registration
- Token refresh
"""

import asyncio
import json
import secrets
import time
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlencode, urlparse
import base64
import hashlib

from fastapi import FastAPI, Request, Response, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
import uvicorn
import httpx

app = FastAPI(title="Mock OAuth MCP Server", version="1.0.0")

# In-memory storage (use a real database in production)
clients = {}
authorization_codes = {}
access_tokens = {}
refresh_tokens = {}

# Server configuration
AUTHORIZATION_ENDPOINT = "http://localhost:8080/oauth/authorize"
TOKEN_ENDPOINT = "http://localhost:8080/oauth/token"
REGISTRATION_ENDPOINT = "http://localhost:8080/oauth/register"
MCP_ENDPOINT = "http://localhost:8080/mcp"

@app.get("/")
async def root():
    """Root endpoint with OAuth discovery headers"""
    return Response(
        content=json.dumps({
            "name": "Mock OAuth MCP Server",
            "version": "1.0.0",
            "description": "Test server for MCP OAuth Bridge development",
            "mcp_endpoint": MCP_ENDPOINT
        }),
        headers={
            "WWW-Authenticate": f'Bearer realm="{MCP_ENDPOINT}", '
                               f'authorization_uri="{AUTHORIZATION_ENDPOINT}", '
                               f'token_uri="{TOKEN_ENDPOINT}"',
            "Content-Type": "application/json"
        }
    )

@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata():
    """OAuth 2.0 Authorization Server Metadata (RFC 8414)"""
    return {
        "issuer": "http://localhost:8080",
        "authorization_endpoint": AUTHORIZATION_ENDPOINT,
        "token_endpoint": TOKEN_ENDPOINT,
        "registration_endpoint": REGISTRATION_ENDPOINT,
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["read", "write", "admin"],
        "service_documentation": "https://example.com/docs"
    }

@app.post("/oauth/register")
async def register_client(request: Request):
    """Dynamic Client Registration (RFC 7591)"""
    try:
        data = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Generate client credentials
    client_id = f"client_{secrets.token_urlsafe(16)}"
    client_secret = secrets.token_urlsafe(32)
    
    # Store client
    clients[client_id] = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uris": data.get("redirect_uris", ["http://localhost:8081/oauth/callback", "urn:ietf:wg:oauth:2.0:oob"]),
        "client_name": data.get("client_name", "MCP OAuth Bridge Client"),
        "scope": data.get("scope", "read write"),
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"]
    }
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_id_issued_at": int(time.time()),
        "client_secret_expires_at": 0,  # Never expires
        "redirect_uris": clients[client_id]["redirect_uris"],
        "grant_types": clients[client_id]["grant_types"],
        "response_types": clients[client_id]["response_types"],
        "token_endpoint_auth_method": "client_secret_post"
    }

@app.get("/oauth/authorize")
async def authorize(
    client_id: str,
    redirect_uri: str,
    response_type: str = "code",
    scope: Optional[str] = None,
    state: Optional[str] = None,
    code_challenge: Optional[str] = None,
    code_challenge_method: Optional[str] = None
):
    """OAuth Authorization Endpoint"""
    
    # Validate client
    if client_id not in clients:
        raise HTTPException(status_code=400, detail="Invalid client_id")
    
    client = clients[client_id]
    
    # Validate redirect URI
    if redirect_uri not in client["redirect_uris"]:
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")
    
    # Validate PKCE
    if not code_challenge or code_challenge_method != "S256":
        raise HTTPException(status_code=400, detail="PKCE required")
    
    # For testing, auto-approve (in real scenarios, show user consent)
    # Generate authorization code
    auth_code = secrets.token_urlsafe(32)
    authorization_codes[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope or "read",
        "code_challenge": code_challenge,
        "expires_at": time.time() + 600,  # 10 minutes
        "user_id": "test_user"
    }
    
    # Handle out-of-band flow
    if redirect_uri == "urn:ietf:wg:oauth:2.0:oob":
        # Return authorization code directly to user
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authorization Code</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }}
                .code {{ background: #f8f9fa; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 16px; margin: 20px 0; border: 2px solid #007bff; }}
                .success {{ color: #28a745; }}
                .instructions {{ background: #e9ecef; padding: 15px; border-radius: 4px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">✅ Authorization Successful</h1>
                <p>Your authorization has been approved for the MCP OAuth Bridge.</p>
                
                <h3>Authorization Code:</h3>
                <div class="code" id="auth-code">{auth_code}</div>
                
                <div class="instructions">
                    <h4>Instructions:</h4>
                    <ol>
                        <li>Copy the authorization code above</li>
                        <li>Return to your terminal</li>
                        <li>Paste the code when prompted</li>
                        <li>Press Enter to complete the authorization</li>
                    </ol>
                </div>
                
                <p><strong>Note:</strong> This code will expire in 10 minutes.</p>
                
                <button onclick="copyCode()" style="background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin-top: 10px;">
                    Copy Code to Clipboard
                </button>
            </div>
            
            <script>
                function copyCode() {{
                    const code = document.getElementById('auth-code').textContent;
                    navigator.clipboard.writeText(code).then(function() {{
                        alert('Authorization code copied to clipboard!');
                    }}, function() {{
                        alert('Failed to copy. Please select and copy manually.');
                    }});
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    # Regular redirect flow
    # Build redirect URL
    params = {"code": auth_code}
    if state:
        params["state"] = state
    
    redirect_url = f"{redirect_uri}?{urlencode(params)}"
    return RedirectResponse(url=redirect_url)

@app.post("/oauth/token")
async def token_endpoint(
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None)
):
    """OAuth Token Endpoint"""
    
    if grant_type == "authorization_code":
        # Authorization code flow
        if not code or not redirect_uri or not client_id or not code_verifier:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Validate authorization code
        if code not in authorization_codes:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        auth_data = authorization_codes[code]
        
        # Check expiration
        if time.time() > auth_data["expires_at"]:
            del authorization_codes[code]
            raise HTTPException(status_code=400, detail="Authorization code expired")
        
        # Validate client
        if auth_data["client_id"] != client_id:
            raise HTTPException(status_code=400, detail="Client mismatch")
        
        # Validate PKCE
        code_challenge = auth_data["code_challenge"]
        expected_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        if code_challenge != expected_challenge:
            raise HTTPException(status_code=400, detail="Invalid code_verifier")
        
        # Generate tokens
        access_token = secrets.token_urlsafe(32)
        refresh_token_value = secrets.token_urlsafe(32)
        
        # Store tokens
        access_tokens[access_token] = {
            "client_id": client_id,
            "user_id": auth_data["user_id"],
            "scope": auth_data["scope"],
            "expires_at": time.time() + 3600  # 1 hour
        }
        
        refresh_tokens[refresh_token_value] = {
            "client_id": client_id,
            "user_id": auth_data["user_id"],
            "scope": auth_data["scope"]
        }
        
        # Clean up authorization code
        del authorization_codes[code]
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh_token_value,
            "scope": auth_data["scope"]
        }
    
    elif grant_type == "refresh_token":
        # Refresh token flow
        if not refresh_token or not client_id:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Validate refresh token
        if refresh_token not in refresh_tokens:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        refresh_data = refresh_tokens[refresh_token]
        
        # Validate client
        if refresh_data["client_id"] != client_id:
            raise HTTPException(status_code=400, detail="Client mismatch")
        
        # Generate new access token
        access_token = secrets.token_urlsafe(32)
        
        access_tokens[access_token] = {
            "client_id": client_id,
            "user_id": refresh_data["user_id"],
            "scope": refresh_data["scope"],
            "expires_at": time.time() + 3600  # 1 hour
        }
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": refresh_data["scope"]
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant_type")

def validate_token(authorization: str) -> Dict[str, Any]:
    """Validate Bearer token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization[7:]  # Remove "Bearer "
    
    if token not in access_tokens:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    token_data = access_tokens[token]
    
    # Check expiration
    if time.time() > token_data["expires_at"]:
        del access_tokens[token]
        raise HTTPException(status_code=401, detail="Access token expired")
    
    return token_data

@app.api_route("/mcp/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def mcp_endpoint(path: str, request: Request):
    """Mock MCP endpoint that requires OAuth"""
    
    # Validate OAuth token
    authorization = request.headers.get("authorization", "")
    token_data = validate_token(authorization)
    
    # Mock MCP response based on the request
    if request.method == "POST":
        try:
            body = await request.json()
        except:
            body = {}
        
        # Mock MCP JSON-RPC response
        if body.get("method") == "tools/call":
            return {
                "jsonrpc": "2.0",
                "id": body.get("id", 1),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Mock response from OAuth MCP Server! "
                                   f"User: {token_data['user_id']}, "
                                   f"Scope: {token_data['scope']}, "
                                   f"Tool: {body.get('params', {}).get('name', 'unknown')}"
                        }
                    ]
                }
            }
        
        # Default response for other methods
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", 1),
            "result": {
                "message": "OAuth authentication successful",
                "user": token_data['user_id'],
                "scope": token_data['scope'],
                "method": body.get("method", "unknown")
            }
        }
    
    # GET request
    return {
        "message": "OAuth MCP Server is working!",
        "user": token_data['user_id'],
        "scope": token_data['scope'],
        "path": path
    }

@app.get("/status")
async def status():
    """Server status endpoint"""
    return {
        "status": "running",
        "clients": len(clients),
        "active_tokens": len(access_tokens),
        "endpoints": {
            "authorization": AUTHORIZATION_ENDPOINT,
            "token": TOKEN_ENDPOINT,
            "registration": REGISTRATION_ENDPOINT,
            "mcp": MCP_ENDPOINT
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Mock OAuth MCP Server on http://localhost:8080")
    print("📋 Endpoints:")
    print(f"  • OAuth Metadata: http://localhost:8080/.well-known/oauth-authorization-server")
    print(f"  • Registration: {REGISTRATION_ENDPOINT}")
    print(f"  • Authorization: {AUTHORIZATION_ENDPOINT}")
    print(f"  • Token: {TOKEN_ENDPOINT}")
    print(f"  • MCP: {MCP_ENDPOINT}")
    print("🔧 Use this URL with your OAuth bridge:")
    print("  mcp-oauth-bridge add mock http://localhost:8080")
    
    uvicorn.run(app, host="localhost", port=8080) 