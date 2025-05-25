"""
Token encryption and storage for MCP OAuth Bridge

Handles secure local storage of OAuth tokens with encryption.
Tokens are encrypted using a key derived from the system and user.
"""

import json
import os
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import socket


@dataclass
class TokenData:
    """OAuth token data structure"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[str] = None
    scope: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if the token is expired"""
        if not self.expires_at:
            return False
        
        try:
            expiry = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            return datetime.now(timezone.utc) >= expiry
        except (ValueError, AttributeError):
            return False
    
    def expires_soon(self, minutes: int = 5) -> bool:
        """Check if token expires within the given minutes"""
        if not self.expires_at:
            return False
        
        try:
            expiry = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            soon = datetime.now(timezone.utc).timestamp() + (minutes * 60)
            return expiry.timestamp() <= soon
        except (ValueError, AttributeError):
            return False


class TokenStorage:
    """Secure token storage with encryption"""
    
    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize token storage
        
        Args:
            config_dir: Custom config directory, defaults to ~/.mcp-oauth-bridge
        """
        self.config_dir = config_dir or Path.home() / ".mcp-oauth-bridge"
        self.tokens_file = self.config_dir / "tokens.enc"
        self._fernet = self._create_cipher()
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
    
    def _create_cipher(self) -> Fernet:
        """Create encryption cipher using system-derived key"""
        # Create a deterministic but secure key based on system characteristics
        # This allows the same key to be generated on subsequent runs
        username = getpass.getuser()
        hostname = socket.gethostname()
        
        # Use a combination of username and hostname as password
        password = f"{username}@{hostname}".encode()
        
        # Use a fixed salt (not ideal for multi-user systems but acceptable for local use)
        # In production, you might want to store a random salt separately
        salt = b"mcp_oauth_bridge_salt_v1"
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    def _load_tokens(self) -> Dict[str, TokenData]:
        """Load and decrypt tokens from storage"""
        if not self.tokens_file.exists():
            return {}
        
        try:
            with open(self.tokens_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data = self._fernet.decrypt(encrypted_data)
            tokens_dict = json.loads(decrypted_data.decode())
            
            # Convert back to TokenData objects
            tokens = {}
            for server_name, token_dict in tokens_dict.items():
                tokens[server_name] = TokenData(**token_dict)
            
            return tokens
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load tokens: {e}")
            print("Token storage may be corrupted or from a different system")
            return {}
    
    def _save_tokens(self, tokens: Dict[str, TokenData]) -> None:
        """Encrypt and save tokens to storage"""
        try:
            # Convert TokenData objects to dict for JSON serialization
            tokens_dict = {
                server_name: asdict(token) 
                for server_name, token in tokens.items()
            }
            
            # Serialize to JSON
            json_data = json.dumps(tokens_dict, indent=2).encode()
            
            # Encrypt the data
            encrypted_data = self._fernet.encrypt(json_data)
            
            # Ensure directory exists
            self.config_dir.mkdir(exist_ok=True)
            
            # Write encrypted tokens
            with open(self.tokens_file, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            print(f"❌ Error saving tokens: {e}")
            raise
    
    def store_token(self, server_name: str, token_data: TokenData) -> None:
        """Store token for a server
        
        Args:
            server_name: Name of the server
            token_data: Token data to store
        """
        tokens = self._load_tokens()
        tokens[server_name] = token_data
        self._save_tokens(tokens)
    
    def get_token(self, server_name: str) -> Optional[TokenData]:
        """Get token for a server
        
        Args:
            server_name: Name of the server
            
        Returns:
            Token data or None if not found
        """
        tokens = self._load_tokens()
        return tokens.get(server_name)
    
    def remove_token(self, server_name: str) -> bool:
        """Remove token for a server
        
        Args:
            server_name: Name of the server
            
        Returns:
            True if token was removed, False if not found
        """
        tokens = self._load_tokens()
        if server_name in tokens:
            del tokens[server_name]
            self._save_tokens(tokens)
            return True
        return False
    
    def list_tokens(self) -> Dict[str, TokenData]:
        """Get all stored tokens
        
        Returns:
            Dictionary of server names to token data
        """
        return self._load_tokens()
    
    def update_token(self, server_name: str, **updates: Any) -> bool:
        """Update specific fields of a stored token
        
        Args:
            server_name: Name of the server
            **updates: Fields to update
            
        Returns:
            True if token was updated, False if not found
        """
        tokens = self._load_tokens()
        if server_name not in tokens:
            return False
        
        token = tokens[server_name]
        
        # Update fields that exist in TokenData
        for field, value in updates.items():
            if hasattr(token, field):
                setattr(token, field, value)
        
        self._save_tokens(tokens)
        return True
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens that cannot be refreshed
        
        Returns:
            Number of tokens removed
        """
        tokens = self._load_tokens()
        expired_servers = []
        
        for server_name, token in tokens.items():
            # Only remove if expired AND no refresh token
            if token.is_expired() and not token.refresh_token:
                expired_servers.append(server_name)
        
        for server_name in expired_servers:
            del tokens[server_name]
        
        if expired_servers:
            self._save_tokens(tokens)
        
        return len(expired_servers)


# Alias for compatibility
TokenManager = TokenStorage 