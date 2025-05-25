# 🔐 MCP OAuth Bridge

**Eliminate OAuth complexity for MCP servers with OpenAI and Anthropic APIs**

A local Python tool that automatically handles OAuth 2.1 authentication for MCP (Model Context Protocol) servers, letting you integrate authenticated APIs with **zero OAuth code required**.

## 🎯 The Problem

Many powerful MCP servers require OAuth authentication (Stripe, Shopify, GitHub, etc.), but integrating them with AI APIs is complex:

```python
# ❌ Before: 50+ lines of OAuth boilerplate per MCP server
client_id = "your_stripe_client_id"
client_secret = "your_stripe_secret" 
auth_url = "https://connect.stripe.com/oauth/authorize"
# ... PKCE generation, state parameters, callback handling
# ... Token storage, refresh logic, error handling
# ... Different OAuth flows for each provider
```

## ✅ The Solution

With MCP OAuth Bridge, it's **one command**:

```bash
# Add any OAuth-enabled MCP server
mcp-oauth-bridge add stripe https://mcp.stripe.com

# Start the bridge
mcp-oauth-bridge start

# Use immediately with any AI API - OAuth handled automatically! 🎉
```

## 🚀 Quick Start

### Installation

```bash
pip install mcp-oauth-bridge
mcp-oauth-bridge init
```

### Add Your First OAuth MCP Server

```bash
# Example: Add Stripe MCP server
mcp-oauth-bridge add stripe https://mcp.stripe.com

# ✅ Automatically discovers OAuth endpoints
# ✅ Opens browser for one-time authorization  
# ✅ Stores encrypted tokens locally
# ✅ Ready to use!
```

### Start the Bridge

```bash
mcp-oauth-bridge start
# 🚀 MCP OAuth Bridge starting on http://localhost:3000
# 📋 Approval UI available at http://localhost:3000/approvals
# 🔧 Configured servers: stripe
```

## 💡 Real-World Examples

### With OpenAI GPT-4

```python
from openai import OpenAI

client = OpenAI()

# Use OAuth-protected MCP servers directly in GPT-4
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Create a $50 payment link for my course"}
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "stripe_create_payment_link",
            "description": "Create Stripe payment link",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "description": {"type": "string"}
                }
            }
        }
    }],
    tool_choice="auto"
)

# The bridge automatically:
# ✅ Injects OAuth tokens
# ✅ Handles token refresh  
# ✅ Forwards requests to Stripe MCP server
# ✅ Returns authenticated responses
```

### With Anthropic Claude

```python
import anthropic

client = anthropic.Anthropic()

# Use multiple OAuth MCP servers with Claude
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Check my Shopify orders and create a GitHub issue for any returns"}
    ],
    tools=[
        {
            "name": "shopify_get_orders",
            "description": "Get recent Shopify orders",
            "input_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                    "status": {"type": "string"}
                }
            }
        },
        {
            "name": "github_create_issue", 
            "description": "Create GitHub issue",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "body": {"type": "string"}
                }
            }
        }
    ]
)

# Both Shopify and GitHub MCP servers are OAuth-protected
# The bridge handles authentication for both automatically! 🎯
```

### Direct MCP Server Access

```bash
# Test any configured server directly
curl -X POST http://localhost:3000/mcp/stripe/payment-links \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "create_payment_link",
      "arguments": {"amount": 5000, "currency": "usd"}
    }
  }'

# Returns authenticated response from Stripe! 
# OAuth token automatically injected by the bridge
```

## 🛠 How It Works

1. **📡 OAuth Discovery**: Automatically discovers OAuth endpoints using RFC standards
2. **🔐 Secure Authorization**: Handles OAuth 2.1 + PKCE authorization flow  
3. **💾 Token Management**: Stores encrypted tokens locally, refreshes automatically
4. **🚀 HTTP Proxy**: Runs local proxy that injects OAuth tokens
5. **🔄 API Translation**: Converts between OpenAI/Anthropic formats and MCP protocol
6. **✅ Approval System**: Optional approval UI for sensitive operations

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenAI/       │    │  MCP OAuth       │    │   OAuth MCP     │
│   Anthropic     │───▶│  Bridge          │───▶│   Server        │
│   API Call      │    │  (localhost:3000)│    │   (Stripe/etc)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌──────────────────┐
                       │ Encrypted Token  │
                       │ Storage          │
                       │ (~/.mcp-oauth-   │
                       │  bridge/)        │
                       └──────────────────┘
```

## 🌟 Key Features

### 🔒 **Enterprise-Grade Security**
- OAuth 2.1 compliance with PKCE
- Encrypted local token storage
- Automatic token refresh
- No network transmission of secrets

### 🚀 **Zero Configuration**
- Standards-based OAuth discovery (RFC 8414, RFC 9728)
- Dynamic client registration (RFC 7591)
- Works with any compliant OAuth provider

### 🔌 **Universal Compatibility**
- **OpenAI GPT-4**: Direct tool integration
- **Anthropic Claude**: Native MCP server support
- **Any HTTP client**: REST API access

### 🎛 **Developer Experience**
- One command to add servers
- Automatic browser authorization
- Built-in approval UI
- Comprehensive logging

## 📋 Commands Reference

```bash
# Initialize configuration
mcp-oauth-bridge init

# Add OAuth MCP server
mcp-oauth-bridge add <name> <url>
mcp-oauth-bridge add stripe https://mcp.stripe.com
mcp-oauth-bridge add shopify https://mcp.shopify.com

# Start the bridge proxy
mcp-oauth-bridge start [--host localhost] [--port 3000]

# Manage servers
mcp-oauth-bridge list                    # List configured servers
mcp-oauth-bridge status                  # Show bridge status
mcp-oauth-bridge remove <name>           # Remove server
mcp-oauth-bridge refresh <name>          # Refresh OAuth token

# Get help
mcp-oauth-bridge --help
```

## 🔧 Configuration

### Default Locations
- **Config**: `~/.mcp-oauth-bridge/config.json`
- **Tokens**: `~/.mcp-oauth-bridge/tokens.enc` (encrypted)
- **Proxy**: `http://localhost:3000`
- **Approval UI**: `http://localhost:3000/approvals`

### Server Configuration
Each server supports:
- **OAuth endpoints**: Auto-discovered or manual
- **Approval policies**: `always_ask`, `always_allow`, `never_allow`
- **Tool-specific policies**: Per-tool approval settings
- **Token refresh**: Automatic when expires

## 🌐 Supported OAuth Providers

Works with any OAuth 2.0/2.1 compliant provider:

- ✅ **Stripe** - Payment processing
- ✅ **Shopify** - E-commerce platform  
- ✅ **GitHub** - Code repositories
- ✅ **Google APIs** - Drive, Calendar, Gmail
- ✅ **Microsoft Graph** - Office 365
- ✅ **Salesforce** - CRM platform
- ✅ **Any RFC-compliant provider**

## 🔍 Testing & Development

### Mock OAuth Server
For development and testing:

```bash
# Start mock OAuth MCP server
python tests/mock_oauth_server.py

# Add to bridge
mcp-oauth-bridge add mock http://localhost:8080

# Test end-to-end
curl -X POST http://localhost:3000/mcp/mock/test \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call"}'
```

### Automated Testing
```bash
# Run complete test suite
python tests/test_oauth_flow.py

# Test specific functionality
pytest tests/ -v
```

## 🤝 Why MCP OAuth Bridge?

### **For AI Developers**
- **Faster Integration**: Minutes instead of hours per OAuth provider
- **Consistent API**: Same pattern for all OAuth MCP servers  
- **Production Ready**: Enterprise security and reliability
- **Future Proof**: Standards-based, works with new providers

### **For MCP Server Providers**
- **Lower Barrier**: Developers can integrate easily
- **Better Adoption**: Remove OAuth complexity obstacle
- **Standard Compliance**: Follow OAuth 2.1 best practices
- **Developer Experience**: Focus on functionality, not auth

### **For Enterprises**
- **Security First**: Local token storage, encrypted secrets
- **Audit Trail**: Full request/response logging
- **Access Control**: Granular approval policies
- **Compliance**: OAuth 2.1, PKCE, industry standards

## 📈 Use Cases

### **AI-Powered Business Automation**
```python
# "Send weekly sales report from Shopify to Slack"
# Bridge handles: Shopify OAuth + Slack OAuth automatically
```

### **Multi-Platform Integration**  
```python
# "Create GitHub issues for Stripe payment failures"
# Bridge handles: Multiple OAuth tokens seamlessly
```

### **Customer Support Automation**
```python
# "Look up customer in Salesforce and create support ticket"
# Bridge handles: Enterprise OAuth with proper token refresh
```

## 🚀 Getting Started Today

1. **Install**: `pip install mcp-oauth-bridge`
2. **Initialize**: `mcp-oauth-bridge init`  
3. **Add Server**: `mcp-oauth-bridge add myapi https://api.example.com`
4. **Start Bridge**: `mcp-oauth-bridge start`
5. **Use with AI**: Point OpenAI/Anthropic to `localhost:3000`

**That's it!** No OAuth code, no token management, no complexity. Just working authenticated MCP servers. 🎉

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤖 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Made with ❤️ for the MCP and AI developer community**

*Eliminate OAuth complexity. Focus on building amazing AI applications.* 🚀
