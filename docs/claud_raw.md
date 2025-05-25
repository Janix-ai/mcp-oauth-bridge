MVP PRD: MCP OAuth Bridge (Open Source)
🎯 MVP Goal
Build a local Python tool that eliminates OAuth complexity for Claude developers. One command to add any authenticated MCP server, zero OAuth code required.
🚀 Core Value Proposition
Before: 50+ lines of OAuth code per MCP server
After: One command → Works with Claude immediately

🛠 What We're Building
The Complete Flow:
Developer installs our Python package
Runs one command to add an OAuth-enabled MCP server
OAuth happens automatically (browser opens, they authorize, tokens saved locally)
Proxy starts on localhost:3000
Developer points Claude to localhost instead of the real MCP server
Our tool handles OAuth tokens + approval UI automatically
📋 MVP Features (Must Have)
1. CLI Tool
pip install mcp-oauth-bridge

# Initialize 
mcp-oauth-bridge init

# Add server with automatic OAuth
mcp-oauth-bridge add stripe https://mcp.stripe.com
# Opens browser, handles OAuth, saves tokens locally

# Start proxy server
mcp-oauth-bridge start
# Runs on localhost:3000

2. OAuth Flow Handler
Automatic discovery: Parse WWW-Authenticate headers, fetch OAuth metadata
PKCE implementation: Generate code challenges, handle security properly
Token management: Store tokens locally (encrypted), handle refresh automatically
Browser integration: Open OAuth URLs, handle callbacks
3. HTTP Proxy Server
Routes: localhost:3000/mcp/{server-name} proxies to real MCP servers
Authentication: Automatically inject OAuth tokens into requests
Error handling: Refresh expired tokens, retry requests
Logging: Basic request/response logging for debugging
4. Approval System
Web UI: Simple approval interface at localhost:3000/approvals
Request queue: Queue tool calls that need approval
Approval flow: Show tool name, arguments, approve/deny buttons
Policies: Per-server approval settings (always allow, always ask, never allow)
5. Local Configuration
Config file: ~/.mcp-oauth-bridge/config.json for server settings
Token storage: ~/.mcp-oauth-bridge/tokens.json (encrypted)
Approval policies: Per-tool approval settings
📁 File Structure
mcp-oauth-bridge/
├── setup.py
├── README.md
├── mcp_oauth_bridge/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── oauth.py            # OAuth flow handling
│   ├── proxy.py            # HTTP proxy server
│   ├── approvals.py        # Approval system
│   ├── config.py           # Configuration management
│   └── tokens.py           # Token encryption/storage
└── templates/
    └── approvals.html      # Simple approval UI

👨‍💻 Developer Experience
Installation & Setup
pip install mcp-oauth-bridge
mcp-oauth-bridge init
# Creates ~/.mcp-oauth-bridge/ directory and config files

Adding First Server
mcp-oauth-bridge add stripe https://mcp.stripe.com
# Output:
# 🔍 Discovering OAuth server for https://mcp.stripe.com...
# 🌐 Opening browser for Stripe authorization...
# ✅ Authorization successful! Tokens saved.
# ✅ Server 'stripe' added to configuration.

Starting the Bridge
mcp-oauth-bridge start
# Output:
# 🚀 MCP OAuth Bridge starting on http://localhost:3000
# 📋 Approval UI available at http://localhost:3000/approvals
# 🔧 Configured servers: stripe

Using with Claude
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    mcp_servers=[{
        "type": "url",
        "url": "http://localhost:3000/mcp/stripe",  # Our proxy
        "name": "stripe"
    }],
    messages=[{"role": "user", "content": "Create a $50 payment link"}]
)

🔒 Security Features (MVP)
Token Security
Local encryption: Tokens encrypted with user-specific key
No network transmission: Tokens never leave user's machine
Automatic refresh: Handle token expiration transparently
Approval System
Default policy: All tool calls require approval
Granular control: Per-server and per-tool approval settings
Clear visibility: Show exactly what Claude wants to do before execution
Error Handling
OAuth failures: Clear error messages, retry mechanisms
Token expiration: Automatic refresh with fallback to re-authorization
Network issues: Graceful degradation and error reporting
✅ Success Metrics (MVP)
Technical Success
[ ] Successfully OAuth with 3+ real MCP servers (Stripe, Shopify, etc.)
[ ] Handle token refresh automatically
[ ] Approval system works end-to-end
[ ] Zero OAuth code required from developers
Community Success
[ ] 50+ GitHub stars in first month
[ ] 10+ developers successfully using it
[ ] 5+ community issues/discussions
[ ] Positive feedback in MCP Discord
🚧 What's NOT in MVP
Won't Build (Yet)
❌ Multi-user support
❌ Web-based configuration UI
❌ Enterprise features (audit logs, team management)
❌ Hosted service
❌ Advanced approval policies
❌ Custom OAuth providers
❌ Docker containers
🎯 Definition of Done
MVP is complete when:
A developer can install the package with pip install
Add an OAuth MCP server with one command
Use it with Claude immediately with zero OAuth code
Approve/deny tool calls through simple web UI
Tool handles token refresh automatically
Works with at least 2 real MCP servers (Stripe + one other)
📅 Timeline: 5-7 days
Day 1: Foundation
CLI structure and basic commands
Configuration file management
Basic project setup
Day 2-3: OAuth Implementation
OAuth discovery and metadata parsing
PKCE implementation
Token storage and encryption
Browser integration for auth flow
Day 4: Proxy Server
HTTP proxy implementation
Request forwarding with token injection
Error handling and retry logic
Day 5: Approval System
Web UI for approvals
Request queuing and management
Approval policies
Day 6-7: Integration & Testing
End-to-end testing with real MCP servers
Documentation and examples
Package preparation for PyPI
🚀 Launch Strategy
Week 1: Build MVP
Week 2: Test with real MCP servers, write docs
Week 3: Launch on GitHub, post to MCP Discord
Week 4: Gather feedback, iterate quickly
This MVP solves the exact OAuth pain point that's blocking Claude developers today, with minimal complexity and maximum impact.
Great question! Let me break down both approaches:
Option 1: Pure Open Source (Recommended for MVP)
How it works:
No Janix servers involved - everything runs locally on developer's machine
Direct OAuth - your tool talks directly to the real OAuth providers (Stripe, Google, etc.)
Local proxy - runs on localhost:3000 and handles everything locally
Architecture:
Claude → http://localhost:3000/mcp/stripe → [Your Tool] → OAuth Flow → Stripe's OAuth → Stripe's MCP Server

What developers get:
# Install your tool
pip install mcp-oauth-bridge

# Add a server (runs OAuth flow locally)
mcp-oauth-bridge add stripe https://mcp.stripe.com
# Opens browser, you authorize with Stripe directly
# Tool saves encrypted tokens locally

# Start proxy
mcp-oauth-bridge start
# Runs on localhost:3000

# Use with Claude
# Point Claude to localhost:3000/mcp/stripe instead of mcp.stripe.com

Pros:
✅ Zero infrastructure costs for you
✅ Maximum privacy - no tokens go through your servers
✅ Faster to build - no server management
✅ Easier adoption - developers just pip install
✅ Open source credibility - truly self-hosted
Cons:
❌ Each developer runs their own OAuth flows
❌ No centralized management for enterprises
❌ Harder to monetize directly
Option 2: Janix OAuth Service
How it works:
Janix manages OAuth - you become the OAuth intermediary
Your servers handle token management and refresh
Developers get API keys from you, not direct OAuth
Architecture:
Claude → https://bridge.janix.ai/mcp/stripe → [Your Servers] → Stripe's MCP Server

What developers get:
# Sign up for Janix account
janix signup

# Add servers through your dashboard
janix add-server stripe --authorize
# Redirects to your OAuth flow, managed by Janix

# Use with Claude
# Point Claude to bridge.janix.ai/mcp/stripe

Pros:
✅ Easier for developers - they don't run anything locally
✅ Enterprise features - centralized management, audit logs
✅ Direct monetization - can charge for usage
✅ Better UX - no local setup required
Cons:
❌ Infrastructure costs - you need servers, databases, security
❌ Trust issues - tokens flow through your servers
❌ Slower to market - more complex to build
❌ Compliance burden - you're handling OAuth tokens
My Recommendation: Start with Option 1
Here's why:
For MVP Success:
Ship faster - no server infrastructure to build
Build trust - developers prefer self-hosted for security
Prove demand - see if people actually use it
Learn the edge cases - understand OAuth complexity without server management burden
Future Path:
Month 1: Open source local tool
Month 2: Add usage analytics, community feedback
Month 3: Launch hosted version as premium option
Month 4: Add enterprise features to hosted version

How Open Source Works:
Developer Experience:
# Install
pip install mcp-oauth-bridge

# First time setup
mcp-oauth-bridge init
# Creates config file locally

# Add authenticated MCP server
mcp-oauth-bridge add-server stripe https://mcp.stripe.com
# Opens browser, you OAuth with Stripe directly
# Tool encrypts and stores tokens locally (~/.mcp-oauth-bridge/tokens.json)

# Start the proxy
mcp-oauth-bridge start
# Runs on localhost:3000
# Shows approval UI at localhost:3000/approvals

# Use with Claude
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    mcp_servers=[{
        "type": "url", 
        "url": "http://localhost:3000/mcp/stripe",  # Your local proxy
        "name": "stripe"
    }],
    messages=[{"role": "user", "content": "Create payment link"}]
)

What You Build:
Python package that handles OAuth flows locally
Local web server for proxy and approvals
Token management with local encryption
Configuration system for managing multiple servers
Business Model:
Open source tool builds community and proves demand
Hosted version for enterprises who want managed service
Consulting/support for complex implementations
Enterprise features (audit logs, team management, etc.)
Start with the open source approach. It's faster to build, easier to adopt, and gives you the best foundation for understanding the market before building the infrastructure-heavy hosted version.

