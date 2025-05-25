"""
Command-line interface for MCP OAuth Bridge

Provides commands for:
- Initializing the bridge configuration
- Adding OAuth-enabled MCP servers
- Starting the proxy server
- Managing servers and tokens
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import Optional

import click
import uvicorn

from .config import Config
from .oauth import OAuthHandler
from .discovery import OAuthDiscovery
from .proxy import ProxyServer, run_proxy_server
from .tokens import TokenManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def main():
    """MCP OAuth Bridge - Local OAuth bridge for MCP servers supporting OpenAI and Anthropic APIs"""
    pass


@main.command()
@click.option('--config-dir', default=None, help='Custom configuration directory')
def init(config_dir: Optional[str]):
    """Initialize MCP OAuth Bridge configuration"""
    try:
        config = Config(config_dir)
        
        # Create configuration directory if it doesn't exist
        config_path = Path(config.config_dir)
        config_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty configuration
        config.save()
        
        click.echo(f"✅ MCP OAuth Bridge initialized!")
        click.echo(f"📁 Configuration directory: {config.config_dir}")
        click.echo(f"🔧 Config file: {config.config_file}")
        click.echo(f"🔑 Tokens file: {config.tokens_file}")
        click.echo("")
        click.echo("Next steps:")
        click.echo("1. Add an MCP server: mcp-oauth-bridge add <name> <url>")
        click.echo("2. Start the proxy: mcp-oauth-bridge start")
        
    except Exception as e:
        click.echo(f"❌ Error initializing configuration: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('name')
@click.argument('url')
@click.option('--config-dir', default=None, help='Custom configuration directory')
@click.option('--no-browser', is_flag=True, help='Don\'t open browser for OAuth')
def add(name: str, url: str, config_dir: Optional[str], no_browser: bool):
    """Add an OAuth-enabled MCP server"""
    try:
        config = Config(config_dir)
        
        # Ensure configuration is initialized
        if not os.path.exists(config.config_file):
            click.echo("❌ Configuration not initialized. Run 'mcp-oauth-bridge init' first.")
            sys.exit(1)
        
        click.echo(f"🔍 Discovering OAuth server for {url}...")
        
        # Run discovery and OAuth flow
        asyncio.run(_add_server_async(name, url, config, no_browser))
        
    except KeyboardInterrupt:
        click.echo("\n⚠️ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error adding server: {e}", err=True)
        sys.exit(1)


async def _add_server_async(name: str, url: str, config: Config, no_browser: bool):
    """Async helper for adding a server"""
    try:
        # Initialize discovery
        discovery = OAuthDiscovery()
        oauth_handler = OAuthHandler(config)
        token_manager = TokenManager(config)
        
        # Discover OAuth configuration
        oauth_config = await discovery.discover_oauth_server(url)
        if not oauth_config:
            click.echo(f"❌ Could not discover OAuth configuration for {url}")
            click.echo("Make sure the server supports OAuth 2.0 and returns proper WWW-Authenticate headers")
            return
        
        click.echo(f"📋 Found authorization server: {oauth_config['authorization_endpoint']}")
        
        # Attempt dynamic client registration if supported
        client_config = None
        if oauth_config.get('registration_endpoint'):
            click.echo("🔧 Attempting dynamic client registration...")
            client_config = await oauth_handler.register_client(oauth_config)
            if client_config:
                click.echo("✅ Client registered successfully")
            else:
                click.echo("⚠️ Dynamic client registration failed, using default client")
        
        # Perform OAuth flow
        if not no_browser:
            click.echo("🌐 Opening browser for authorization...")
        
        token = await oauth_handler.authorize_server(oauth_config, client_config, not no_browser)
        if not token:
            click.echo("❌ OAuth authorization failed")
            return
        
        # Store server configuration
        server_config = {
            'name': name,
            'url': url,
            'oauth_config': oauth_config,
            'client_config': client_config
        }
        
        config.add_server(name, server_config)
        config.save()
        
        # Store token
        token_manager.store_token(name, token)
        
        click.echo("✅ Authorization successful! Tokens saved.")
        click.echo(f"✅ Server '{name}' added to configuration.")
        click.echo("")
        click.echo("You can now start the proxy server:")
        click.echo("mcp-oauth-bridge start")
        
    except Exception as e:
        click.echo(f"❌ Error in server setup: {e}")
        raise


@main.command()
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=3000, help='Port to bind to')
@click.option('--config-dir', default=None, help='Custom configuration directory')
def start(host: str, port: int, config_dir: Optional[str]):
    """Start the MCP OAuth Bridge proxy server"""
    try:
        config = Config(config_dir)
        
        # Ensure configuration is initialized
        if not os.path.exists(config.config_file):
            click.echo("❌ Configuration not initialized. Run 'mcp-oauth-bridge init' first.")
            sys.exit(1)
        
        # Start the proxy server
        asyncio.run(run_proxy_server(config_dir, host, port))
        
    except KeyboardInterrupt:
        click.echo("\n🛑 Shutting down...")
    except Exception as e:
        click.echo(f"❌ Error starting proxy server: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--config-dir', default=None, help='Custom configuration directory')
def list(config_dir: Optional[str]):
    """List configured MCP servers"""
    try:
        config = Config(config_dir)
        
        if not os.path.exists(config.config_file):
            click.echo("❌ Configuration not initialized. Run 'mcp-oauth-bridge init' first.")
            sys.exit(1)
        
        servers = config.servers
        if not servers:
            click.echo("📭 No servers configured.")
            click.echo("Add a server with: mcp-oauth-bridge add <name> <url>")
            return
        
        click.echo("🔧 Configured servers:")
        for server_name, server_config in servers.items():
            url = server_config.get('url', 'Unknown')
            click.echo(f"  • {server_name}: {url}")
        
        click.echo(f"\n📊 Total: {len(servers)} server(s)")
        
    except Exception as e:
        click.echo(f"❌ Error listing servers: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('name')
@click.option('--config-dir', default=None, help='Custom configuration directory')
def remove(name: str, config_dir: Optional[str]):
    """Remove a configured MCP server"""
    try:
        config = Config(config_dir)
        token_manager = TokenManager(config)
        
        if not os.path.exists(config.config_file):
            click.echo("❌ Configuration not initialized. Run 'mcp-oauth-bridge init' first.")
            sys.exit(1)
        
        if name not in config.servers:
            click.echo(f"❌ Server '{name}' not found.")
            sys.exit(1)
        
        # Confirm removal
        if not click.confirm(f"Remove server '{name}'? This will delete stored tokens."):
            click.echo("Cancelled.")
            return
        
        # Remove server and tokens
        config.remove_server(name)
        config.save()
        token_manager.remove_token(name)
        
        click.echo(f"✅ Server '{name}' removed successfully.")
        
    except Exception as e:
        click.echo(f"❌ Error removing server: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--config-dir', default=None, help='Custom configuration directory')
def status(config_dir: Optional[str]):
    """Show MCP OAuth Bridge status"""
    try:
        config = Config(config_dir)
        token_manager = TokenManager(config)
        
        if not os.path.exists(config.config_file):
            click.echo("❌ Configuration not initialized. Run 'mcp-oauth-bridge init' first.")
            return
        
        click.echo("📊 MCP OAuth Bridge Status")
        click.echo("=" * 40)
        
        # Configuration info
        click.echo(f"📁 Config directory: {config.config_dir}")
        click.echo(f"🌐 Proxy URL: {config.proxy_url}")
        
        # Server info
        servers = config.servers
        click.echo(f"🔧 Configured servers: {len(servers)}")
        
        if servers:
            click.echo("\nServers:")
            for server_name, server_config in servers.items():
                url = server_config.get('url', 'Unknown')
                
                # Check token status
                token = token_manager.get_token(server_name)
                if token:
                    token_status = "✅ Valid token"
                else:
                    token_status = "❌ No token"
                
                click.echo(f"  • {server_name}: {url} ({token_status})")
        
        # Check if proxy is running
        click.echo(f"\n🚀 To start proxy: mcp-oauth-bridge start")
        click.echo(f"📋 Approval UI will be at: {config.proxy_url}/approvals")
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('name')
@click.option('--config-dir', default=None, help='Custom configuration directory')
@click.option('--no-browser', is_flag=True, help='Don\'t open browser for OAuth')
def refresh(name: str, config_dir: Optional[str], no_browser: bool):
    """Refresh OAuth token for a server"""
    try:
        config = Config(config_dir)
        
        if not os.path.exists(config.config_file):
            click.echo("❌ Configuration not initialized. Run 'mcp-oauth-bridge init' first.")
            sys.exit(1)
        
        if name not in config.servers:
            click.echo(f"❌ Server '{name}' not found.")
            sys.exit(1)
        
        # Run token refresh
        asyncio.run(_refresh_token_async(name, config, no_browser))
        
    except Exception as e:
        click.echo(f"❌ Error refreshing token: {e}", err=True)
        sys.exit(1)


async def _refresh_token_async(name: str, config: Config, no_browser: bool):
    """Async helper for refreshing token"""
    try:
        oauth_handler = OAuthHandler(config)
        token_manager = TokenManager(config)
        
        server_config = config.get_server(name)
        current_token = token_manager.get_token(name)
        
        if current_token and current_token.get('refresh_token'):
            click.echo(f"🔄 Refreshing token for '{name}'...")
            new_token = await oauth_handler.refresh_token(
                server_config['oauth_config'], 
                current_token['refresh_token']
            )
            
            if new_token:
                token_manager.store_token(name, new_token)
                click.echo("✅ Token refreshed successfully!")
                return
        
        # Fall back to full re-authorization
        click.echo(f"🔄 Re-authorizing with '{name}'...")
        if not no_browser:
            click.echo("🌐 Opening browser for authorization...")
        
        token = await oauth_handler.authorize_server(
            server_config['oauth_config'], 
            server_config.get('client_config'),
            not no_browser
        )
        
        if token:
            token_manager.store_token(name, token)
            click.echo("✅ Re-authorization successful!")
        else:
            click.echo("❌ Re-authorization failed")
            
    except Exception as e:
        click.echo(f"❌ Error refreshing token: {e}")
        raise


if __name__ == '__main__':
    main() 