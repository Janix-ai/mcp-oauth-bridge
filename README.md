# MCP OAuth Bridge

> **One command to add any OAuth-enabled MCP server. Zero OAuth code required.**

A local Python tool that eliminates OAuth complexity for developers using MCP servers with both OpenAI and Anthropic APIs. Built with full OAuth 2.1 compliance and automatic server discovery.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Standards Compliant](https://img.shields.io/badge/OAuth-2.1%20RFC%209728-orange.svg)](https://datatracker.ietf.org/doc/html/rfc9728)

## 🎯 Problem Solved

**Before**: Adding OAuth to MCP servers requires 50+ lines of OAuth code per server, plus separate integration for each AI API.

**After**: One command → Works with both OpenAI and Anthropic immediately, with zero OAuth code required.

```bash
mcp-oauth-bridge add stripe https://mcp.stripe.com  # OAuth happens automatically
mcp-oauth-bridge start                              # Works with any AI API
```

## 🚀 Quick Start

### Installation

```bash
# Install via pip
pip install mcp-oauth-bridge

# Or install from source
git clone https://github.com/your-org/mcp-oauth-bridge
cd mcp-oauth-bridge
pip install -e .
```

### Basic Setup

```bash
# 1. Initialize configuration
mcp-oauth-bridge init

# 2. Add your first OAuth-enabled MCP server
mcp-oauth-bridge add stripe https://mcp.stripe.com
# 🔍 Discovering OAuth server...
# 📋 Found authorization server: https://auth.stripe.com
# 🌐 Opening browser for authorization...
# ✅ Authorization successful! Tokens saved.

# 3. Start the bridge
mcp-oauth-bridge start
# 🚀 MCP OAuth Bridge starting on http://localhost:3000
# 📋 Approval UI available at http://localhost:3000/approvals
# 🔧 Configured servers: stripe
```

### Using with AI APIs

#### OpenAI Responses API

```python
from openai import OpenAI

client = OpenAI()
response = client.responses.create(
    model="gpt-4.1",
    tools=[{
        "type": "mcp",
        "server_label": "stripe",
        "server_url": "http://localhost:3000/mcp/stripe",  # Our proxy
        "require_approval": "never"  # We handle approvals locally
    }],
    input="Create a $50 payment link for my product"
)

print(response.choices[0].message.content)
```

#### Anthropic Messages API

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    mcp_servers=[{
        "type": "url",
        "url": "http://localhost:3000/mcp/stripe",  # Our proxy
        "name": "stripe"
        # No authorization_token needed - our proxy handles it
    }],
    messages=[{"role": "user", "content": "Create a $50 payment link"}],
    extra_headers={"anthropic-beta": "mcp-client-2025-04-04"}
)

print(response.content[0].text)
```

## ✨ Features

### 🔐 **Standards-Compliant OAuth 2.1**
- **PKCE Required**: All OAuth flows use PKCE for security
- **Auto Discovery**: RFC9728 OAuth Protected Resource Metadata
- **Dynamic Registration**: RFC7591 OAuth Dynamic Client Registration
- **Token Refresh**: Automatic token refresh per OAuth 2.1 spec

### 🌐 **Multi-API Support**
- **OpenAI Integration**: Native support for OpenAI Responses API
- **Anthropic Integration**: Native support for Anthropic Messages API  
- **Request Translation**: Seamless conversion between API formats
- **Error Handling**: Unified error handling across both APIs

### 🛡️ **Secure Local-First Design**
- **Encrypted Storage**: Tokens encrypted with system-derived keys
- **No Network Transmission**: Tokens never leave your machine
- **Local Proxy**: All OAuth handled locally on localhost:3000
- **Zero Dependencies**: No external services required

### 📋 **Unified Approval System**
- **Web UI**: Clean approval interface at `/approvals`
- **Granular Control**: Per-server and per-tool approval policies
- **Request Queue**: Queue and batch approve tool calls
- **OpenAI Integration**: Works with OpenAI's built-in approval system

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI API        │    │  MCP OAuth      │    │  OAuth MCP      │
│ (OpenAI/Claude) │◄──►│     Bridge      │◄──►│    Servers      │
│                 │    │  (localhost)    │    │ (Stripe/etc)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │ Approval UI │
                       │ (Browser)   │
                       └─────────────┘
```

### Core Components

- **Proxy Server**: FastAPI-based HTTP proxy on localhost:3000
- **OAuth Handler**: Standards-compliant OAuth 2.1 implementation
- **Discovery Engine**: Automatic OAuth server discovery
- **Token Manager**: Encrypted local token storage
- **API Adapters**: OpenAI and Anthropic API format adapters
- **Approval Manager**: Web-based tool call approval system

## 📚 Usage Guide

### Managing Servers

```bash
# List configured servers
mcp-oauth-bridge list
# 🔧 Configured servers:
#   • stripe: https://mcp.stripe.com
#   • shopify: https://mcp.shopify.com

# Check system status
mcp-oauth-bridge status
# 📊 MCP OAuth Bridge Status
# 📁 Config directory: /Users/you/.mcp-oauth-bridge
# 🌐 Proxy URL: http://localhost:3000
# 🔧 Configured servers: 2

# Remove a server
mcp-oauth-bridge remove stripe
# Remove server 'stripe'? This will delete stored tokens. [y/N]: y
# ✅ Server 'stripe' removed successfully.

# Refresh OAuth token
mcp-oauth-bridge refresh stripe
# 🔄 Refreshing token for 'stripe'...
# ✅ Token refreshed successfully!
```

### Advanced Configuration

#### Custom Configuration Directory

```bash
# Use custom config directory
mcp-oauth-bridge --config-dir /path/to/config init
mcp-oauth-bridge --config-dir /path/to/config start
```

#### Custom Proxy Settings

```bash
# Start on different host/port
mcp-oauth-bridge start --host 0.0.0.0 --port 8080
```

#### Headless OAuth (No Browser)

```bash
# Add server without opening browser
mcp-oauth-bridge add myserver https://api.example.com --no-browser
# 🔍 Discovering OAuth server for https://api.example.com...
# Please visit: https://auth.example.com/oauth/authorize?client_id=...
```

### Popular MCP Servers

```bash
# Financial Services
mcp-oauth-bridge add stripe https://mcp.stripe.com
mcp-oauth-bridge add square https://mcp.squareup.com

# E-commerce
mcp-oauth-bridge add shopify https://mcp.shopify.com  
mcp-oauth-bridge add woocommerce https://mcp.woocommerce.com

# Communication
mcp-oauth-bridge add twilio https://your-function.twil.io/mcp
mcp-oauth-bridge add slack https://mcp.slack.com

# Development Tools
mcp-oauth-bridge add github https://mcp.github.com
mcp-oauth-bridge add gitlab https://mcp.gitlab.com
```

## 🔧 API Reference

### Proxy Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/mcp/{server}/{path}` | ALL | Proxy to MCP server with OAuth |
| `/openai/responses` | POST | OpenAI Responses API integration |
| `/anthropic/messages` | POST | Anthropic Messages API integration |
| `/approvals` | GET | Approval management UI |
| `/approvals/{id}/approve` | POST | Approve tool call |
| `/approvals/{id}/deny` | POST | Deny tool call |
| `/config/servers` | GET | List configured servers |

### Configuration File Format

```json
{
  "version": "1.0",
  "proxy_host": "localhost",
  "proxy_port": 3000,
  "servers": {
    "stripe": {
      "name": "stripe",
      "url": "https://mcp.stripe.com",
      "oauth_config": {
        "authorization_endpoint": "https://auth.stripe.com/oauth/authorize",
        "token_endpoint": "https://auth.stripe.com/oauth/token",
        "registration_endpoint": "https://auth.stripe.com/oauth/register",
        "scopes_supported": ["read", "write"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"]
      },
      "client_config": {
        "client_id": "your_client_id",
        "client_secret": null
      }
    }
  }
}
```

## 🔒 Security & Privacy

### OAuth 2.1 Compliance

- **PKCE Required**: All authorization flows use PKCE per OAuth 2.1 draft spec
- **Dynamic Registration**: Secure client registration when supported by servers  
- **HTTPS Enforcement**: All OAuth endpoints must use HTTPS
- **Secure Token Storage**: Tokens encrypted with PBKDF2-derived keys

### Local-First Security

- **No Cloud Dependencies**: Everything runs locally on your machine
- **Encrypted Token Storage**: Tokens encrypted with system-specific keys
- **Ephemeral Sessions**: Browser sessions cleared after OAuth completion
- **Localhost Only**: Proxy binds only to localhost by default

### Authorization Server Discovery

- **Standards-Based**: Uses WWW-Authenticate headers per RFC9728
- **Metadata Validation**: Validates OAuth 2.0 Authorization Server Metadata (RFC8414)
- **Secure Endpoint Resolution**: Verifies all discovered endpoints use HTTPS

## 🐛 Troubleshooting

### Common Issues

#### OAuth Discovery Failed
```bash
# Error: Could not discover OAuth configuration
# Solution: Check if server supports OAuth 2.0 and returns WWW-Authenticate headers
curl -I https://your-mcp-server.com
# Look for: WWW-Authenticate: Bearer realm="..."
```

#### Token Refresh Failed
```bash
# Error: Token refresh failed
# Solution: Re-authorize with the server
mcp-oauth-bridge refresh server-name
# Or remove and re-add the server
mcp-oauth-bridge remove server-name
mcp-oauth-bridge add server-name https://server-url.com
```

#### Port Already in Use
```bash
# Error: Port 3000 is already in use
# Solution: Use a different port
mcp-oauth-bridge start --port 8080
```

#### Token Storage Corrupted
```bash
# Error: Could not load tokens
# Solution: Remove corrupted token file
rm ~/.mcp-oauth-bridge/tokens.enc
# Then re-authorize servers
mcp-oauth-bridge refresh server-name
```

### Debug Mode

```bash
# Enable debug logging
export PYTHONPATH=/path/to/mcp-oauth-bridge
python -m mcp_oauth_bridge.cli start --debug
```

## 👥 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/mcp-oauth-bridge
cd mcp-oauth-bridge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black mcp_oauth_bridge/
isort mcp_oauth_bridge/
mypy mcp_oauth_bridge/
```

### Project Structure

```
mcp-oauth-bridge/
├── mcp_oauth_bridge/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── proxy.py            # HTTP proxy server
│   ├── oauth.py            # OAuth 2.1 implementation
│   ├── discovery.py        # OAuth server discovery
│   ├── config.py           # Configuration management
│   ├── tokens.py           # Token encryption/storage
│   ├── approvals.py        # Approval system
│   └── adapters/
│       ├── openai.py       # OpenAI API adapter
│       └── anthropic.py    # Anthropic API adapter
├── templates/
│   └── approvals.html      # Approval UI template
├── docs/                   # Documentation
├── tests/                  # Test suite
├── pyproject.toml          # Project configuration
└── README.md
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📋 Roadmap

### MVP (Current)
- [x] OAuth 2.1 with PKCE implementation
- [x] OpenAI and Anthropic API support
- [x] Local proxy server
- [x] Token encryption and storage
- [x] Web-based approval system
- [x] CLI interface

### Future Enhancements
- [ ] Docker container support
- [ ] Multi-user configuration
- [ ] Advanced approval policies
- [ ] Webhook support for token refresh
- [ ] Integration with more AI APIs
- [ ] Plugin system for custom adapters

## 🤝 Community

- **Issues**: [GitHub Issues](https://github.com/your-org/mcp-oauth-bridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/mcp-oauth-bridge/discussions)
- **Discord**: [MCP Community Discord](https://discord.gg/mcp)

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

**Built with ❤️ for the MCP and AI developer community**
