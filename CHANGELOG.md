# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-27

### Added
- Initial release of MCP OAuth Bridge
- OAuth 2.1 + PKCE authentication flow support
- Local proxy server for MCP servers
- Encrypted token storage and automatic refresh
- OpenAI and Anthropic API compatibility
- Command-line interface for server management
- Web-based approval system for sensitive operations
- Automatic OAuth endpoint discovery
- Support for multiple MCP servers
- Comprehensive documentation and examples

### Security
- Encrypted local token storage using cryptography library
- PKCE (Proof Key for Code Exchange) implementation
- Secure token refresh mechanism
- No network transmission of OAuth secrets

[Unreleased]: https://github.com/scottmsilver/mcp-oauth-bridge/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/scottmsilver/mcp-oauth-bridge/releases/tag/v0.1.0 