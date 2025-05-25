# Contributing to MCP OAuth Bridge

Thank you for your interest in contributing to MCP OAuth Bridge! This project aims to eliminate OAuth complexity for MCP server integration, and we welcome contributions from developers of all skill levels.

## 🎯 Project Vision

Our goal is to make OAuth-protected MCP servers as easy to use as API key-protected ones. Every contribution should support this mission of **eliminating complexity for developers**.

## 🚀 Quick Start for Contributors

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mcp-oauth-bridge.git
   cd mcp-oauth-bridge
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev,test]"
   ```

4. **Verify the installation**
   ```bash
   mcp-oauth-bridge --help
   pytest tests/ -v
   ```

## 🛠 Development Workflow

### Before You Start
- Check existing [issues](https://github.com/your-org/mcp-oauth-bridge/issues) to see if your idea is already being worked on
- For major changes, please open an issue first to discuss the approach
- Look for issues labeled `good first issue` if you're new to the project

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**
   - Write clear, readable code
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run the test suite
   pytest tests/ -v
   
   # Test with the mock server
   python tests/mock_oauth_server.py &
   python tests/test_oauth_flow.py
   
   # Test CLI functionality
   mcp-oauth-bridge init
   mcp-oauth-bridge add mock http://localhost:8080
   mcp-oauth-bridge start
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new OAuth provider support"
   # Use conventional commit format (see below)
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Code Style and Standards

### Python Code Style
- **Black** for code formatting: `black mcp_oauth_bridge/`
- **isort** for import sorting: `isort mcp_oauth_bridge/`
- **Type hints** for all public functions
- **Docstrings** for all modules, classes, and public functions

### Commit Message Format
We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat: add support for GitHub OAuth provider
fix: handle token refresh errors gracefully
docs: update README with new installation instructions
test: add integration tests for Shopify MCP server
```

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions and classes
   - Mock external dependencies
   - Fast execution

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use the mock OAuth server
   - Test end-to-end workflows

3. **Manual Testing**
   - Test with real OAuth providers
   - Verify CLI functionality
   - Check UI components

### Writing Tests

```python
# Good test example
def test_oauth_discovery_success():
    """Test successful OAuth server discovery."""
    discovery = OAuthDiscovery()
    config = discovery.discover_oauth_config("http://localhost:8080")
    
    assert config is not None
    assert config["authorization_endpoint"] == "http://localhost:8080/oauth/authorize"
    assert config["token_endpoint"] == "http://localhost:8080/oauth/token"

# Test naming convention: test_[component]_[scenario]_[expected_result]
```

### Test Requirements
- All new features must include tests
- Aim for >90% code coverage
- Tests should be deterministic and fast
- Use descriptive test names and docstrings

## 📚 Documentation

### What Needs Documentation
- **README.md**: User-facing documentation
- **API Documentation**: Function/class docstrings
- **Code Comments**: Complex logic explanation
- **Examples**: Real-world usage examples

### Documentation Style
- Use clear, simple language
- Include code examples for complex features
- Update examples when APIs change
- Add troubleshooting for common issues

## 🔒 Security Guidelines

### Security Best Practices
- **Never commit secrets**: Use environment variables or config files
- **Validate all inputs**: Especially OAuth parameters
- **Follow OAuth 2.1 specs**: Security is paramount for auth systems
- **Report security issues privately**: Email security@yourproject.com

### OAuth Security
- Always use PKCE for authorization flows
- Validate redirect URIs strictly
- Implement proper token storage encryption
- Handle token refresh securely

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues for duplicates
2. Test with the latest version
3. Try reproducing with minimal example

### Good Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command `mcp-oauth-bridge add...`
2. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. macOS 14.0]
- Python version: [e.g. 3.11.5]
- MCP OAuth Bridge version: [e.g. 0.1.0]

**Additional context**
Logs, screenshots, or other helpful information.
```

## ✨ Feature Requests

### What Makes a Good Feature Request
- **Clear use case**: Why is this needed?
- **Specific requirements**: What exactly should it do?
- **Backward compatibility**: How does it affect existing users?
- **Implementation ideas**: Any thoughts on approach?

### Feature Request Process
1. Open an issue with the `enhancement` label
2. Discuss the approach with maintainers
3. Get approval before starting implementation
4. Create a pull request with tests and documentation

## 🎯 Areas for Contribution

### High-Priority Areas
- **OAuth Provider Support**: Add support for new OAuth providers
- **Error Handling**: Improve error messages and recovery
- **Documentation**: Examples, tutorials, troubleshooting guides
- **Testing**: More comprehensive test coverage
- **Performance**: Optimize token refresh and request handling

### Good First Issues
- Fix typos in documentation
- Add configuration validation
- Improve CLI help messages
- Add more unit tests
- Update dependency versions

### Advanced Contributions
- New OAuth flow implementations
- API adapter improvements
- Security enhancements
- Performance optimizations

## 🤝 Code Review Process

### What Reviewers Look For
- **Functionality**: Does it work as intended?
- **Code Quality**: Is it readable and maintainable?
- **Tests**: Are there adequate tests?
- **Documentation**: Is it properly documented?
- **Security**: Are there any security concerns?

### Getting Your PR Reviewed
- Keep PRs focused and reasonably sized
- Write clear PR descriptions
- Respond to feedback promptly
- Be open to suggestions and changes

## 🏷 Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] Run full test suite
- [ ] Create release notes
- [ ] Tag and publish to PyPI

## 🌟 Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes for significant contributions
- Given commit access for sustained, quality contributions

## 💬 Getting Help

### Where to Ask Questions
- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Discord**: Real-time chat (link in README)

### Response Times
- We aim to respond to issues within 48 hours
- Complex PRs may take longer to review
- Security issues get priority attention

## 📄 License

By contributing to MCP OAuth Bridge, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to MCP OAuth Bridge!** 

Together, we're making OAuth integration as simple as it should be. 🚀 