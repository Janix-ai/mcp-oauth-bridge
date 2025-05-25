# Testing the MCP OAuth Bridge

Since most real MCP servers use API keys rather than OAuth, we've created test infrastructure to validate the OAuth bridge functionality.

## 🧪 Test Infrastructure

### Mock OAuth MCP Server
The `mock_oauth_server.py` creates a fully compliant OAuth 2.1 server that implements:

- **OAuth 2.1 with PKCE** - Complete authorization code flow
- **Dynamic Client Registration** - RFC 7591 compliant
- **Token Refresh** - Automatic token renewal
- **MCP Protocol** - Mock MCP endpoints that require OAuth
- **Standards Compliance** - RFC 8414 metadata, RFC 9728 discovery

## 🚀 Quick Test

### Option 1: Automated Test
```bash
# Run the complete test suite
python tests/test_oauth_flow.py
```

### Option 2: Manual Testing

#### Step 1: Start Mock Server
```bash
# Terminal 1: Start the mock OAuth MCP server
python tests/mock_oauth_server.py

# Output:
# 🚀 Starting Mock OAuth MCP Server on http://localhost:8080
# 📋 Endpoints:
#   • OAuth Metadata: http://localhost:8080/.well-known/oauth-authorization-server
#   • Registration: http://localhost:8080/oauth/register
#   • Authorization: http://localhost:8080/oauth/authorize
#   • Token: http://localhost:8080/oauth/token
#   • MCP: http://localhost:8080/mcp
```

#### Step 2: Test OAuth Discovery
```bash
# Verify OAuth discovery works
curl -I http://localhost:8080/
# Look for: WWW-Authenticate: Bearer realm=...

# Check OAuth metadata
curl http://localhost:8080/.well-known/oauth-authorization-server | jq
```

#### Step 3: Setup OAuth Bridge
```bash
# Terminal 2: Initialize and configure the bridge
mcp-oauth-bridge init
mcp-oauth-bridge add mock http://localhost:8080

# This will:
# 🔍 Discover OAuth server
# 🔧 Register OAuth client
# 🌐 Open browser for authorization
# ✅ Store encrypted tokens
```

#### Step 4: Start Bridge
```bash
mcp-oauth-bridge start

# Output:
# 🚀 MCP OAuth Bridge starting on http://localhost:3000
# 📋 Approval UI available at http://localhost:3000/approvals
# 🔧 Configured servers: mock
```

#### Step 5: Test End-to-End
```bash
# Terminal 3: Test the complete flow
curl -X POST http://localhost:3000/mcp/mock/test \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "test_tool",
      "arguments": {"message": "Hello OAuth!"}
    }
  }'

# Should return OAuth-authenticated response
```

## 🔍 Testing Scenarios

### 1. OAuth Discovery
```bash
# Test WWW-Authenticate header
curl -I http://localhost:8080/

# Test OAuth metadata endpoint
curl http://localhost:8080/.well-known/oauth-authorization-server
```

### 2. Dynamic Client Registration
```bash
# Test client registration
curl -X POST http://localhost:8080/oauth/register \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Test Client",
    "redirect_uris": ["http://localhost:3000/oauth/callback"]
  }'
```

### 3. Token Refresh
```bash
# Bridge automatically handles token refresh
# Tokens expire after 1 hour in the mock server

# Force token refresh test
mcp-oauth-bridge refresh mock
```

### 4. Approval System
```bash
# Visit approval UI
open http://localhost:3000/approvals

# Test approval API
curl -X POST http://localhost:3000/approvals/123/approve
```

## 🎯 What Gets Tested

### OAuth 2.1 Compliance
- ✅ PKCE code challenge/verifier
- ✅ Authorization code flow  
- ✅ Token refresh flow
- ✅ Dynamic client registration
- ✅ Standards-based discovery

### MCP Integration
- ✅ OAuth token injection
- ✅ Request forwarding
- ✅ Error handling
- ✅ Token expiration handling

### Multi-API Support
- ✅ OpenAI format conversion
- ✅ Anthropic format conversion
- ✅ Approval system integration

## 🐛 Troubleshooting

### Mock Server Issues
```bash
# Check if server is running
curl http://localhost:8080/status

# Restart if needed
pkill -f mock_oauth_server.py
python tests/mock_oauth_server.py
```

### Bridge Issues
```bash
# Check bridge status
mcp-oauth-bridge status

# Reset configuration
rm -rf ~/.mcp-oauth-bridge
mcp-oauth-bridge init
```

### Token Issues
```bash
# Check stored tokens
mcp-oauth-bridge list

# Refresh tokens
mcp-oauth-bridge refresh mock

# Re-authorize if needed
mcp-oauth-bridge remove mock
mcp-oauth-bridge add mock http://localhost:8080
```

## 🔧 Real-World Testing

Once the mock server tests pass, try with these OAuth providers:

### GitHub (has OAuth, could wrap in MCP)
```bash
# Create GitHub OAuth app
# https://github.com/settings/applications/new

# Add to bridge
mcp-oauth-bridge add github https://api.github.com
```

### Google (OAuth provider, wrap APIs in MCP)
```bash
# Create Google OAuth app  
# https://console.developers.google.com/

# Add to bridge
mcp-oauth-bridge add google https://your-mcp-wrapper.com
```

### Custom OAuth MCP Server
If you build a real MCP server with OAuth, test it the same way:

```bash
mcp-oauth-bridge add myserver https://your-server.com
mcp-oauth-bridge start
```

## 📝 Mock Server Features

The mock server provides:

- **Realistic OAuth flows** - Proper PKCE, token refresh
- **MCP compatibility** - Returns valid MCP JSON-RPC responses  
- **Error simulation** - Test 401s, expired tokens, invalid clients
- **Standards compliance** - RFC 8414, RFC 7591, RFC 9728
- **Development friendly** - Clear logging, status endpoints

This gives you a complete testing environment for OAuth bridge development! 🚀 