# MVP PRD: MCP OAuth Bridge (Open Source)

## 🎯 MVP Goal
Build a local Python tool that eliminates OAuth complexity for developers using MCP servers with **both OpenAI and Anthropic APIs**. **One command to add any authenticated MCP server, zero OAuth code required.**

## 🚀 Core Value Proposition
```
Before: 50+ lines of OAuth code per MCP server + API-specific integration
After: One command → Works with both OpenAI and Anthropic immediately
```

## 🛠 What We're Building

### The Complete Flow:
1. **Developer installs** our Python package
2. **Runs one command** to add an OAuth-enabled MCP server  
3. **OAuth happens automatically** (browser opens, they authorize, tokens saved locally)
4. **Proxy starts** on localhost:3000
5. **Developer uses with any AI API** - our tool adapts to OpenAI or Anthropic formats
6. **Our tool handles** OAuth tokens, token refresh, and approval flows automatically

## 📋 MVP Features (Must Have)

### 1. **CLI Tool**
```bash
pip install mcp-oauth-bridge

# Initialize 
mcp-oauth-bridge init

# Add server with automatic OAuth discovery
mcp-oauth-bridge add stripe https://mcp.stripe.com
# Discovers OAuth via WWW-Authenticate headers
# Opens browser, handles OAuth with PKCE, saves tokens locally

# Start proxy server
mcp-oauth-bridge start
# Runs on localhost:3000
```

### 2. **OAuth Flow Handler** (Spec Compliant)
- **Standards-based discovery**: Parse WWW-Authenticate headers, fetch OAuth 2.0 Protected Resource Metadata (RFC9728)
- **Authorization Server Metadata**: Fetch OAuth 2.0 Authorization Server Metadata (RFC8414)
- **Dynamic Client Registration**: Support OAuth 2.0 Dynamic Client Registration (RFC7591) when available
- **PKCE implementation**: Required for security per OAuth 2.1 draft spec
- **Token management**: Store tokens locally (encrypted), handle refresh automatically
- **Browser integration**: Open OAuth URLs, handle callbacks on localhost

### 3. **Multi-API Proxy Server**
- **OpenAI Integration**: Support MCP tools in Responses API format
- **Anthropic Integration**: Support MCP servers in Messages API format
- **Token Injection**: Automatically add OAuth tokens to all MCP requests
- **Error Handling**: Handle 401s, refresh tokens, retry requests
- **Request Translation**: Convert between API formats as needed

### 4. **Unified Approval System**
- **Web UI**: Simple approval interface at `localhost:3000/approvals`
- **OpenAI Compatibility**: Integrate with OpenAI's built-in approval system when available
- **Anthropic Support**: Provide approval UI for Anthropic Messages API
- **Request Queue**: Queue tool calls that need approval
- **Approval Policies**: Per-server approval settings (always allow, always ask, never allow)

### 5. **Local Configuration**
- **Config file**: `~/.mcp-oauth-bridge/config.json` for server settings
- **Token storage**: `~/.mcp-oauth-bridge/tokens.json` (encrypted)
- **API compatibility**: Support both OpenAI and Anthropic usage patterns
- **Approval policies**: Per-tool and per-server approval settings

## 📁 File Structure
```
mcp-oauth-bridge/
├── setup.py
├── pyproject.toml
├── README.md
├── mcp_oauth_bridge/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── oauth.py            # OAuth 2.1 flow handling with PKCE
│   ├── discovery.py        # OAuth server discovery per RFC9728
│   ├── proxy.py            # Multi-API HTTP proxy server
│   ├── approvals.py        # Unified approval system
│   ├── config.py           # Configuration management
│   ├── tokens.py           # Token encryption/storage
│   └── adapters/
│       ├── __init__.py
│       ├── openai.py       # OpenAI Responses API adapter
│       └── anthropic.py    # Anthropic Messages API adapter
└── templates/
    └── approvals.html      # Simple approval UI
```

## 👨‍💻 Developer Experience

### Installation & Setup
```bash
pip install mcp-oauth-bridge
mcp-oauth-bridge init
# Creates ~/.mcp-oauth-bridge/ directory and config files
```

### Adding First Server
```bash
mcp-oauth-bridge add stripe https://mcp.stripe.com
# Output:
# 🔍 Discovering OAuth server for https://mcp.stripe.com...
# 📋 Found authorization server: https://auth.stripe.com
# 🔧 Attempting dynamic client registration...
# ✅ Client registered successfully
# 🌐 Opening browser for Stripe authorization...
# ✅ Authorization successful! Tokens saved.
# ✅ Server 'stripe' added to configuration.
```

### Starting the Bridge
```bash
mcp-oauth-bridge start
# Output:
# 🚀 MCP OAuth Bridge starting on http://localhost:3000
# 📋 Approval UI available at http://localhost:3000/approvals
# 🔧 Configured servers: stripe, shopify
# 🔌 Supporting OpenAI Responses API and Anthropic Messages API
```

### Using with OpenAI
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
    input="Create a $50 payment link"
)
```

### Using with Anthropic
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
```

### Cross-API Usage Examples
```bash
# Add multiple popular servers
mcp-oauth-bridge add shopify https://mcp.shopify.com
mcp-oauth-bridge add twilio https://your-function.twil.io/mcp
mcp-oauth-bridge add deepwiki https://mcp.deepwiki.com/mcp

# Start bridge
mcp-oauth-bridge start

# Now use the same servers with any AI API
```

## 🔒 Security Features (MVP)

### OAuth 2.1 Compliance
- **PKCE required**: All OAuth flows use PKCE for security
- **Secure token storage**: Tokens encrypted with user-specific key derived from system
- **No network transmission**: Tokens never leave user's machine except to authorized servers
- **Automatic refresh**: Handle token expiration transparently
- **Dynamic registration**: Secure client registration when supported

### Authorization Server Discovery
- **Standards-based**: Use WWW-Authenticate headers and RFC9728 metadata
- **Secure validation**: Verify authorization server endpoints and metadata
- **HTTPS enforcement**: All OAuth endpoints must use HTTPS

### Approval System
- **Default security**: All tool calls require approval by default
- **Granular control**: Per-server and per-tool approval settings
- **Clear visibility**: Show exactly what the AI wants to do before execution
- **API integration**: Work with OpenAI's built-in approval system when available

### Error Handling
- **OAuth failures**: Clear error messages, retry mechanisms
- **Token expiration**: Automatic refresh with fallback to re-authorization
- **Network issues**: Graceful degradation and error reporting
- **API compatibility**: Handle different error formats from OpenAI vs Anthropic

## ✅ Success Metrics (MVP)

### Technical Success
- [ ] Successfully OAuth with 3+ real MCP servers (Stripe, Shopify, Twilio)
- [ ] Handle token refresh automatically per OAuth 2.1 spec
- [ ] Support both OpenAI Responses API and Anthropic Messages API
- [ ] Approval system works end-to-end with both APIs
- [ ] Zero OAuth code required from developers
- [ ] Dynamic Client Registration works with supporting servers

### Community Success
- [ ] 100+ GitHub stars in first month
- [ ] 25+ developers successfully using it with real projects
- [ ] 10+ community issues/discussions
- [ ] Positive feedback in MCP Discord and AI dev communities
- [ ] Usage with both OpenAI and Anthropic APIs demonstrated

## 🚧 What's NOT in MVP

### Won't Build (Yet)
- ❌ Multi-user support
- ❌ Web-based configuration UI
- ❌ Enterprise features (audit logs, team management)
- ❌ Hosted service (staying local-first)
- ❌ Advanced approval policies (complex rule engines)
- ❌ Custom OAuth providers beyond standard flows
- ❌ Docker containers/cloud deployment
- ❌ Support for STDIO MCP servers (HTTP/SSE only)

## 🎯 Definition of Done

### MVP is complete when:
1. **A developer can install** the package with `pip install`
2. **Add an OAuth MCP server** with one command using standards-based discovery
3. **Use it with both OpenAI and Anthropic** immediately with zero OAuth code
4. **Approve/deny tool calls** through unified web UI
5. **Tool handles token refresh** automatically per OAuth 2.1 spec
6. **Works with at least 3 real MCP servers** (Stripe, Shopify, + one other)
7. **Demonstrates cross-API compatibility** with examples for both platforms

## 📅 Timeline: 7-10 days

### Day 1-2: Foundation & Discovery
- CLI structure and basic commands
- OAuth server discovery implementation (RFC9728)
- Authorization server metadata fetching (RFC8414)
- Configuration file management
- Basic project setup

### Day 3-4: OAuth Implementation
- OAuth 2.1 flow with PKCE implementation
- Dynamic Client Registration (RFC7591)
- Token storage and encryption
- Browser integration for auth flow
- Token refresh handling

### Day 5-6: Multi-API Proxy Server
- HTTP proxy implementation
- OpenAI Responses API adapter
- Anthropic Messages API adapter
- Request forwarding with token injection
- Error handling and retry logic

### Day 7-8: Approval System
- Unified web UI for approvals
- Integration with OpenAI's approval system
- Request queuing and management
- Approval policies configuration

### Day 9-10: Integration & Testing
- End-to-end testing with real MCP servers
- Cross-API testing (OpenAI + Anthropic)
- Documentation and examples
- Package preparation for PyPI

## 🚀 Launch Strategy

### Week 1-2: Build MVP
- Focus on core functionality and multi-API support
- Test with real servers (Stripe, Shopify, Twilio)

### Week 3: Test & Document
- Comprehensive testing with both OpenAI and Anthropic
- Write detailed documentation and examples
- Create demo videos showing cross-API usage

### Week 4: Launch
- Launch on GitHub with comprehensive README
- Post to MCP Discord, OpenAI community, Anthropic Discord
- Create blog post explaining the OAuth problem and solution
- Submit to relevant newsletters and communities

### Week 5+: Iterate
- Gather feedback from both OpenAI and Anthropic developers
- Add support for additional MCP servers
- Iterate based on community needs

## 🌟 Why This Approach

### Open Source Local-First Benefits
✅ **Zero infrastructure costs** - no servers to maintain
✅ **Maximum privacy** - tokens never leave user's machine  
✅ **Faster to build** - no server management complexity
✅ **Easier adoption** - developers just `pip install`
✅ **Cross-platform compatibility** - works with any AI API
✅ **Standards compliant** - follows OAuth 2.1 and MCP specs

### Future Monetization Path
- **Month 1**: Open source tool builds community
- **Month 2**: Add analytics, gather usage data
- **Month 3**: Launch hosted version for enterprises
- **Month 4**: Add enterprise features (audit logs, team management)

**This MVP solves the exact OAuth pain point blocking developers today, with support for both major AI APIs and full compliance with emerging standards.**