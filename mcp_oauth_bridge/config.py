"""
Configuration management for MCP OAuth Bridge

Handles storing and loading server configurations, approval policies,
and other settings in ~/.mcp-oauth-bridge/
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class ApprovalPolicy(str, Enum):
    """Approval policy options for tool calls"""
    ALWAYS_ALLOW = "always_allow"
    ALWAYS_ASK = "always_ask"
    NEVER_ALLOW = "never_allow"


@dataclass
class ServerConfig:
    """Configuration for a single MCP server"""
    name: str
    url: str
    oauth_config: Dict[str, Any]
    approval_policy: ApprovalPolicy = ApprovalPolicy.ALWAYS_ASK
    tool_approvals: Dict[str, ApprovalPolicy] = None
    
    def __post_init__(self) -> None:
        if self.tool_approvals is None:
            self.tool_approvals = {}


class Config:
    """Main configuration manager for MCP OAuth Bridge"""
    
    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize configuration manager
        
        Args:
            config_dir: Custom config directory, defaults to ~/.mcp-oauth-bridge
        """
        self.config_dir = config_dir or Path.home() / ".mcp-oauth-bridge"
        self.config_file = self.config_dir / "config.json"
        self.servers: Dict[str, ServerConfig] = {}
        self.proxy_port = 3000
        self.proxy_host = "localhost"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load existing configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from config.json"""
        if not self.config_file.exists():
            return
            
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Load proxy settings
            self.proxy_port = data.get("proxy_port", 3000)
            self.proxy_host = data.get("proxy_host", "localhost")
            
            # Load server configurations
            servers_data = data.get("servers", {})
            for name, server_data in servers_data.items():
                # Convert approval policy strings back to enums
                approval_policy = ApprovalPolicy(server_data.get("approval_policy", "always_ask"))
                tool_approvals = {
                    tool: ApprovalPolicy(policy) 
                    for tool, policy in server_data.get("tool_approvals", {}).items()
                }
                
                self.servers[name] = ServerConfig(
                    name=server_data["name"],
                    url=server_data["url"],
                    oauth_config=server_data["oauth_config"],
                    approval_policy=approval_policy,
                    tool_approvals=tool_approvals
                )
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"⚠️  Warning: Could not load config file: {e}")
            print("Using default configuration")
    
    def _save_config(self) -> None:
        """Save current configuration to config.json"""
        # Convert server configs to serializable format
        servers_data = {}
        for name, server in self.servers.items():
            server_dict = asdict(server)
            # Convert enums to strings for JSON serialization
            server_dict["approval_policy"] = server.approval_policy.value
            server_dict["tool_approvals"] = {
                tool: policy.value for tool, policy in server.tool_approvals.items()
            }
            servers_data[name] = server_dict
        
        config_data = {
            "proxy_port": self.proxy_port,
            "proxy_host": self.proxy_host,
            "servers": servers_data
        }
        
        # Ensure directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Write config file
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def add_server(self, server: ServerConfig) -> None:
        """Add or update a server configuration
        
        Args:
            server: Server configuration to add
        """
        self.servers[server.name] = server
        self._save_config()
    
    def remove_server(self, name: str) -> bool:
        """Remove a server configuration
        
        Args:
            name: Name of server to remove
            
        Returns:
            True if server was removed, False if not found
        """
        if name in self.servers:
            del self.servers[name]
            self._save_config()
            return True
        return False
    
    def get_server(self, name: str) -> Optional[ServerConfig]:
        """Get server configuration by name
        
        Args:
            name: Server name
            
        Returns:
            Server configuration or None if not found
        """
        return self.servers.get(name)
    
    def list_servers(self) -> List[str]:
        """Get list of configured server names
        
        Returns:
            List of server names
        """
        return list(self.servers.keys())
    
    def set_approval_policy(self, server_name: str, policy: ApprovalPolicy, tool_name: Optional[str] = None) -> bool:
        """Set approval policy for a server or specific tool
        
        Args:
            server_name: Name of the server
            policy: Approval policy to set
            tool_name: Optional specific tool name, if None sets server default
            
        Returns:
            True if policy was set, False if server not found
        """
        server = self.get_server(server_name)
        if not server:
            return False
        
        if tool_name:
            server.tool_approvals[tool_name] = policy
        else:
            server.approval_policy = policy
        
        self._save_config()
        return True
    
    def get_approval_policy(self, server_name: str, tool_name: Optional[str] = None) -> Optional[ApprovalPolicy]:
        """Get approval policy for a server or specific tool
        
        Args:
            server_name: Name of the server
            tool_name: Optional specific tool name
            
        Returns:
            Approval policy or None if not found
        """
        server = self.get_server(server_name)
        if not server:
            return None
        
        if tool_name and tool_name in server.tool_approvals:
            return server.tool_approvals[tool_name]
        
        return server.approval_policy
    
    def set_proxy_settings(self, host: str = "localhost", port: int = 3000) -> None:
        """Set proxy server settings
        
        Args:
            host: Proxy host
            port: Proxy port
        """
        self.proxy_host = host
        self.proxy_port = port
        self._save_config()
    
    @property
    def proxy_url(self) -> str:
        """Get the proxy server URL"""
        return f"http://{self.proxy_host}:{self.proxy_port}" 