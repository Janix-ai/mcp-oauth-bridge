"""
OAuth 2.1 flow handling with PKCE for MCP OAuth Bridge

Implements OAuth 2.1 authorization code flow with PKCE (RFC 7636),
dynamic client registration (RFC 7591), and token management.
"""

import base64
import hashlib
import secrets
import webbrowser
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
from datetime import datetime, timezone, timedelta
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

from .tokens import TokenData, TokenStorage
from .discovery import OAuthDiscovery


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback"""
    
    def do_GET(self) -> None:
        """Handle GET request to callback endpoint"""
        # Parse callback parameters
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # Store callback data for retrieval
        self.server.callback_params = params
        
        # Send response to browser
        if 'code' in params:
            response = """
            <html>
            <head><title>Authorization Successful</title></head>
            <body>
                <h1>✅ Authorization Successful</h1>
                <p>You can close this window and return to your terminal.</p>
                <script>window.close();</script>
            </body>
            </html>
            """
            self.send_response(200)
        else:
            error = params.get('error', ['unknown'])[0]
            response = f"""
            <html>
            <head><title>Authorization Failed</title></head>
            <body>
                <h1>❌ Authorization Failed</h1>
                <p>Error: {error}</p>
                <p>You can close this window and try again.</p>
                <script>window.close();</script>
            </body>
            </html>
            """
            self.send_response(400)
        
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def log_message(self, format: str, *args: Any) -> None:
        """Suppress log messages"""
        pass


class OAuthHandler:
    """OAuth 2.1 flow handler with PKCE"""
    
    def __init__(self, token_storage: Optional[TokenStorage] = None) -> None:
        """Initialize OAuth handler
        
        Args:
            token_storage: Token storage instance, creates new if None
        """
        self.token_storage = token_storage or TokenStorage()
        self.discovery = OAuthDiscovery()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MCP-OAuth-Bridge/0.1.0'
        })
    
    def _generate_pkce_pair(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and challenge
        
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate code verifier (RFC 7636)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge (S256 method)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def _attempt_dynamic_registration(self, oauth_config: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Attempt dynamic client registration per RFC 7591
        
        Args:
            oauth_config: OAuth configuration from discovery
            
        Returns:
            Client credentials dict or None if registration fails/unavailable
        """
        registration_endpoint = oauth_config.get('registration_endpoint')
        if not registration_endpoint:
            return None
        
        try:
            print(f"🔧 Attempting dynamic client registration...")
            
            # Build registration request
            registration_data = {
                'client_name': 'MCP OAuth Bridge',
                'redirect_uris': ['http://localhost:8080/oauth/callback'],
                'grant_types': ['authorization_code'],
                'response_types': ['code'],
                'token_endpoint_auth_method': 'none',  # Public client
                'application_type': 'native'
            }
            
            response = self.session.post(
                registration_endpoint,
                json=registration_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in (200, 201):
                client_data = response.json()
                print(f"✅ Client registered successfully")
                return {
                    'client_id': client_data['client_id'],
                    'client_secret': client_data.get('client_secret')  # May be None for public clients
                }
            else:
                print(f"⚠️  Dynamic client registration failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️  Dynamic client registration error: {e}")
            return None
    
    def _start_callback_server(self) -> HTTPServer:
        """Start local HTTP server for OAuth callback
        
        Returns:
            HTTPServer instance
        """
        server = HTTPServer(('localhost', 8080), CallbackHandler)
        server.callback_params = None
        
        # Start server in background thread
        def run_server():
            server.serve_forever()
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        
        return server
    
    def authorize_server(self, server_name: str, server_url: str) -> bool:
        """Complete OAuth authorization flow for a server
        
        Args:
            server_name: Name to identify the server
            server_url: MCP server URL
            
        Returns:
            True if authorization successful, False otherwise
        """
        try:
            # Step 1: Discover OAuth configuration
            print(f"🔍 Discovering OAuth configuration for {server_url}...")
            oauth_config = self.discovery.discover_oauth_config(server_url)
            if not oauth_config:
                print(f"❌ Could not discover OAuth configuration for {server_url}")
                return False
            
            # Step 2: Attempt dynamic client registration
            client_credentials = self._attempt_dynamic_registration(oauth_config)
            if not client_credentials:
                print(f"⚠️  Using default client configuration (public client)")
                client_credentials = {
                    'client_id': 'mcp-oauth-bridge',
                    'client_secret': None
                }
            
            # Step 3: Generate PKCE parameters
            code_verifier, code_challenge = self._generate_pkce_pair()
            
            # Step 4: Start callback server
            print(f"🔧 Starting callback server on http://localhost:8080...")
            callback_server = self._start_callback_server()
            
            try:
                # Step 5: Build authorization URL
                state = secrets.token_urlsafe(32)
                auth_params = {
                    'response_type': 'code',
                    'client_id': client_credentials['client_id'],
                    'redirect_uri': 'http://localhost:8080/oauth/callback',
                    'code_challenge': code_challenge,
                    'code_challenge_method': 'S256',
                    'state': state,
                }
                
                # Add scope if available
                scopes = oauth_config.get('scopes_supported')
                if scopes:
                    auth_params['scope'] = ' '.join(scopes[:3])  # Use first few scopes
                
                auth_url = f"{oauth_config['authorization_endpoint']}?{urlencode(auth_params)}"
                
                # Step 6: Open browser for authorization
                print(f"🌐 Opening browser for authorization...")
                print(f"📋 Authorization URL: {auth_url}")
                webbrowser.open(auth_url)
                
                # Step 7: Wait for callback
                print(f"⏳ Waiting for authorization callback...")
                timeout = 300  # 5 minutes
                start_time = time.time()
                
                while callback_server.callback_params is None and (time.time() - start_time) < timeout:
                    time.sleep(0.5)
                
                if callback_server.callback_params is None:
                    print(f"❌ Authorization timeout after {timeout} seconds")
                    return False
                
                callback_params = callback_server.callback_params
                
                # Step 8: Handle callback
                if 'error' in callback_params:
                    error = callback_params['error'][0]
                    error_description = callback_params.get('error_description', [''])[0]
                    print(f"❌ Authorization error: {error}")
                    if error_description:
                        print(f"   Description: {error_description}")
                    return False
                
                if 'code' not in callback_params:
                    print(f"❌ No authorization code received")
                    return False
                
                auth_code = callback_params['code'][0]
                received_state = callback_params.get('state', [''])[0]
                
                # Verify state parameter
                if received_state != state:
                    print(f"❌ State parameter mismatch")
                    return False
                
                # Step 9: Exchange code for tokens
                print(f"🔄 Exchanging authorization code for tokens...")
                token_data = self._exchange_code_for_tokens(
                    oauth_config, client_credentials, auth_code, code_verifier
                )
                
                if not token_data:
                    print(f"❌ Token exchange failed")
                    return False
                
                # Step 10: Store tokens and configuration
                self.token_storage.store_token(server_name, token_data)
                
                print(f"✅ Authorization successful! Tokens saved for server '{server_name}'")
                return True
                
            finally:
                # Clean up callback server
                callback_server.shutdown()
                
        except Exception as e:
            print(f"❌ Authorization error: {e}")
            return False
    
    def _exchange_code_for_tokens(
        self, 
        oauth_config: Dict[str, Any], 
        client_credentials: Dict[str, str], 
        auth_code: str, 
        code_verifier: str
    ) -> Optional[TokenData]:
        """Exchange authorization code for access tokens
        
        Args:
            oauth_config: OAuth configuration
            client_credentials: Client ID and secret
            auth_code: Authorization code from callback
            code_verifier: PKCE code verifier
            
        Returns:
            Token data or None if exchange fails
        """
        try:
            token_data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': 'http://localhost:8080/oauth/callback',
                'code_verifier': code_verifier,
                'client_id': client_credentials['client_id'],
            }
            
            # Add client secret if available (confidential client)
            if client_credentials.get('client_secret'):
                token_data['client_secret'] = client_credentials['client_secret']
            
            response = self.session.post(
                oauth_config['token_endpoint'],
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Token exchange failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
            
            token_response = response.json()
            
            # Calculate expiry time
            expires_at = None
            if 'expires_in' in token_response:
                expires_in = int(token_response['expires_in'])
                expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
            
            return TokenData(
                access_token=token_response['access_token'],
                refresh_token=token_response.get('refresh_token'),
                token_type=token_response.get('token_type', 'Bearer'),
                expires_at=expires_at,
                scope=token_response.get('scope')
            )
            
        except Exception as e:
            print(f"❌ Token exchange error: {e}")
            return None
    
    def refresh_token(self, server_name: str, oauth_config: Dict[str, Any]) -> bool:
        """Refresh access token for a server
        
        Args:
            server_name: Server name
            oauth_config: OAuth configuration
            
        Returns:
            True if refresh successful, False otherwise
        """
        try:
            token_data = self.token_storage.get_token(server_name)
            if not token_data or not token_data.refresh_token:
                return False
            
            print(f"🔄 Refreshing token for server '{server_name}'...")
            
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': token_data.refresh_token,
            }
            
            response = self.session.post(
                oauth_config['token_endpoint'],
                data=refresh_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Token refresh failed: {response.status_code}")
                return False
            
            token_response = response.json()
            
            # Calculate new expiry time
            expires_at = None
            if 'expires_in' in token_response:
                expires_in = int(token_response['expires_in'])
                expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
            
            # Update token data
            new_token_data = TokenData(
                access_token=token_response['access_token'],
                refresh_token=token_response.get('refresh_token', token_data.refresh_token),
                token_type=token_response.get('token_type', 'Bearer'),
                expires_at=expires_at,
                scope=token_response.get('scope', token_data.scope)
            )
            
            self.token_storage.store_token(server_name, new_token_data)
            print(f"✅ Token refreshed successfully for server '{server_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Token refresh error: {e}")
            return False
    
    def get_valid_token(self, server_name: str, oauth_config: Dict[str, Any]) -> Optional[str]:
        """Get a valid access token for a server, refreshing if necessary
        
        Args:
            server_name: Server name
            oauth_config: OAuth configuration
            
        Returns:
            Valid access token or None if unavailable
        """
        token_data = self.token_storage.get_token(server_name)
        if not token_data:
            return None
        
        # Check if token needs refresh
        if token_data.expires_soon(minutes=5):
            if not self.refresh_token(server_name, oauth_config):
                # Refresh failed, token might be invalid
                return None
            # Get updated token data
            token_data = self.token_storage.get_token(server_name)
        
        return token_data.access_token if token_data else None 