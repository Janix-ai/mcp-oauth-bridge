"""
OAuth server discovery for MCP OAuth Bridge

Implements RFC 9728 (OAuth 2.0 Protected Resource Metadata) and RFC 8414 
(OAuth 2.0 Authorization Server Metadata) for automatic discovery of OAuth endpoints.
"""

import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass


@dataclass
class AuthorizationServerMetadata:
    """OAuth 2.0 Authorization Server Metadata from RFC 8414"""
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    registration_endpoint: Optional[str] = None
    revocation_endpoint: Optional[str] = None
    scopes_supported: Optional[List[str]] = None
    response_types_supported: Optional[List[str]] = None
    grant_types_supported: Optional[List[str]] = None
    code_challenge_methods_supported: Optional[List[str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthorizationServerMetadata':
        """Create from discovery response"""
        return cls(
            issuer=data['issuer'],
            authorization_endpoint=data['authorization_endpoint'],
            token_endpoint=data['token_endpoint'],
            registration_endpoint=data.get('registration_endpoint'),
            revocation_endpoint=data.get('revocation_endpoint'),
            scopes_supported=data.get('scopes_supported'),
            response_types_supported=data.get('response_types_supported'),
            grant_types_supported=data.get('grant_types_supported'),
            code_challenge_methods_supported=data.get('code_challenge_methods_supported'),
        )


@dataclass
class ProtectedResourceMetadata:
    """OAuth 2.0 Protected Resource Metadata from RFC 9728"""
    resource: str
    authorization_servers: List[str]
    scopes_supported: Optional[List[str]] = None
    bearer_methods_supported: Optional[List[str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtectedResourceMetadata':
        """Create from discovery response"""
        return cls(
            resource=data['resource'],
            authorization_servers=data['authorization_servers'],
            scopes_supported=data.get('scopes_supported'),
            bearer_methods_supported=data.get('bearer_methods_supported'),
        )


class OAuthDiscovery:
    """OAuth server discovery using RFC standards"""
    
    def __init__(self, timeout: int = 10) -> None:
        """Initialize discovery client
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        # Set a proper User-Agent
        self.session.headers.update({
            'User-Agent': 'MCP-OAuth-Bridge/0.1.0'
        })
    
    def discover_protected_resource(self, resource_url: str) -> Optional[ProtectedResourceMetadata]:
        """Discover OAuth configuration for a protected resource using RFC 9728
        
        Args:
            resource_url: URL of the MCP server
            
        Returns:
            Protected resource metadata or None if not found
        """
        try:
            # Step 1: Try to get protected resource metadata from well-known endpoint
            parsed = urlparse(resource_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            metadata_url = urljoin(base_url, "/.well-known/oauth-protected-resource")
            
            print(f"🔍 Checking protected resource metadata at {metadata_url}")
            response = self.session.get(metadata_url, timeout=self.timeout)
            
            if response.status_code == 200:
                metadata = ProtectedResourceMetadata.from_dict(response.json())
                print(f"✅ Found protected resource metadata")
                return metadata
            
            # Step 2: Try making a request to the resource to get WWW-Authenticate header
            print(f"🔍 Probing resource for WWW-Authenticate header")
            response = self.session.get(resource_url, timeout=self.timeout)
            
            if 'WWW-Authenticate' in response.headers:
                auth_header = response.headers['WWW-Authenticate']
                return self._parse_www_authenticate(auth_header, resource_url)
            
            print(f"⚠️  No OAuth metadata found for {resource_url}")
            return None
            
        except Exception as e:
            print(f"❌ Error discovering protected resource: {e}")
            return None
    
    def _parse_www_authenticate(self, auth_header: str, resource_url: str) -> Optional[ProtectedResourceMetadata]:
        """Parse WWW-Authenticate header for OAuth information
        
        Args:
            auth_header: WWW-Authenticate header value
            resource_url: Original resource URL
            
        Returns:
            Protected resource metadata or None
        """
        try:
            # Simple parsing of Bearer realm parameter
            # Format: Bearer realm="https://auth.example.com", scope="read write"
            if not auth_header.startswith('Bearer'):
                return None
            
            # Extract realm (authorization server)
            realm_start = auth_header.find('realm="')
            if realm_start == -1:
                return None
            
            realm_start += 7  # len('realm="')
            realm_end = auth_header.find('"', realm_start)
            if realm_end == -1:
                return None
            
            auth_server = auth_header[realm_start:realm_end]
            
            # Extract scope if present
            scopes = None
            scope_start = auth_header.find('scope="')
            if scope_start != -1:
                scope_start += 7  # len('scope="')
                scope_end = auth_header.find('"', scope_start)
                if scope_end != -1:
                    scope_str = auth_header[scope_start:scope_end]
                    scopes = scope_str.split()
            
            return ProtectedResourceMetadata(
                resource=resource_url,
                authorization_servers=[auth_server],
                scopes_supported=scopes
            )
            
        except Exception as e:
            print(f"❌ Error parsing WWW-Authenticate header: {e}")
            return None
    
    def discover_authorization_server(self, auth_server_url: str) -> Optional[AuthorizationServerMetadata]:
        """Discover authorization server metadata using RFC 8414
        
        Args:
            auth_server_url: Authorization server base URL
            
        Returns:
            Authorization server metadata or None if not found
        """
        try:
            # RFC 8414: Authorization server metadata endpoint
            metadata_url = urljoin(auth_server_url.rstrip('/'), '/.well-known/oauth-authorization-server')
            
            print(f"🔍 Discovering authorization server metadata at {metadata_url}")
            response = self.session.get(metadata_url, timeout=self.timeout)
            
            if response.status_code == 200:
                metadata = AuthorizationServerMetadata.from_dict(response.json())
                print(f"✅ Found authorization server metadata")
                return metadata
            
            # Fallback: try issuer-specific discovery
            # Some servers use issuer/.well-known/oauth-authorization-server
            if not auth_server_url.endswith('/.well-known/oauth-authorization-server'):
                fallback_url = urljoin(auth_server_url.rstrip('/'), '/.well-known/oauth-authorization-server')
                if fallback_url != metadata_url:
                    print(f"🔍 Trying fallback discovery at {fallback_url}")
                    response = self.session.get(fallback_url, timeout=self.timeout)
                    if response.status_code == 200:
                        metadata = AuthorizationServerMetadata.from_dict(response.json())
                        print(f"✅ Found authorization server metadata")
                        return metadata
            
            print(f"⚠️  No authorization server metadata found at {auth_server_url}")
            return None
            
        except Exception as e:
            print(f"❌ Error discovering authorization server: {e}")
            return None
    
    def discover_oauth_config(self, resource_url: str) -> Optional[Dict[str, Any]]:
        """Complete OAuth discovery process for a resource
        
        Args:
            resource_url: MCP server URL
            
        Returns:
            Complete OAuth configuration or None if discovery fails
        """
        print(f"🔍 Starting OAuth discovery for {resource_url}")
        
        # Step 1: Discover protected resource metadata
        resource_metadata = self.discover_protected_resource(resource_url)
        if not resource_metadata:
            return None
        
        # Step 2: Discover authorization server metadata
        if not resource_metadata.authorization_servers:
            print("❌ No authorization servers found in resource metadata")
            return None
        
        # Use the first authorization server
        auth_server_url = resource_metadata.authorization_servers[0]
        auth_metadata = self.discover_authorization_server(auth_server_url)
        
        if not auth_metadata:
            return None
        
        # Step 3: Validate PKCE support (required for OAuth 2.1)
        pkce_methods = auth_metadata.code_challenge_methods_supported or []
        if 'S256' not in pkce_methods:
            print("⚠️  Warning: Authorization server does not advertise S256 PKCE support")
            print("Proceeding anyway as many servers support it without advertising")
        
        # Step 4: Build complete configuration
        config = {
            'resource_url': resource_url,
            'authorization_endpoint': auth_metadata.authorization_endpoint,
            'token_endpoint': auth_metadata.token_endpoint,
            'registration_endpoint': auth_metadata.registration_endpoint,
            'revocation_endpoint': auth_metadata.revocation_endpoint,
            'issuer': auth_metadata.issuer,
            'scopes_supported': resource_metadata.scopes_supported or auth_metadata.scopes_supported,
            'response_types_supported': auth_metadata.response_types_supported,
            'grant_types_supported': auth_metadata.grant_types_supported,
            'code_challenge_methods_supported': auth_metadata.code_challenge_methods_supported,
        }
        
        print(f"✅ OAuth discovery completed successfully")
        print(f"📋 Authorization endpoint: {auth_metadata.authorization_endpoint}")
        print(f"📋 Token endpoint: {auth_metadata.token_endpoint}")
        if auth_metadata.registration_endpoint:
            print(f"📋 Registration endpoint: {auth_metadata.registration_endpoint}")
        
        return config 