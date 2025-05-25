# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 🚨 **DO NOT** open a public GitHub issue for security vulnerabilities

Instead, please report security vulnerabilities by emailing: **security@mcp-oauth-bridge.com**

### What to include in your report:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker achieve?
- **Reproduction**: Step-by-step instructions to reproduce the issue
- **Environment**: Operating system, Python version, package version
- **Suggested fix**: If you have ideas for how to fix the issue

### What to expect:

1. **Acknowledgment**: We'll acknowledge receipt within 48 hours
2. **Investigation**: We'll investigate and confirm the vulnerability
3. **Timeline**: We'll provide an expected timeline for the fix
4. **Resolution**: We'll release a security patch as soon as possible
5. **Credit**: We'll give you credit in the security advisory (unless you prefer to remain anonymous)

### Security practices in this project:

- **Encrypted token storage**: All OAuth tokens are encrypted at rest using industry-standard cryptography
- **PKCE implementation**: OAuth 2.1 with Proof Key for Code Exchange for enhanced security
- **No secrets in transit**: OAuth secrets never leave your local machine
- **Secure defaults**: All security-sensitive features are enabled by default
- **Regular dependency updates**: We monitor and update dependencies for known vulnerabilities
- **Code scanning**: Automated security scanning with tools like Bandit
- **Principle of least privilege**: The bridge only requests necessary OAuth scopes

### Responsible disclosure:

We follow responsible disclosure practices:
- Security vulnerabilities will not be publicly disclosed until a fix is available
- We'll coordinate with you on the disclosure timeline
- We'll provide advance notice to users before public disclosure when possible

## Security considerations for users:

1. **Keep your installation updated**: Always use the latest version
2. **Secure your environment**: Ensure your local machine is secure
3. **Review OAuth scopes**: Only grant necessary permissions to OAuth applications
4. **Monitor access logs**: Regularly review OAuth access logs in your provider dashboards
5. **Use strong system passwords**: The bridge inherits security from your system's user account

Thank you for helping keep MCP OAuth Bridge secure! 🔒 