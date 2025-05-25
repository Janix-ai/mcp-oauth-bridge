# Publishing to PyPI Guide

This guide covers how to publish `mcp-oauth-bridge` to PyPI.

## Prerequisites

### 1. PyPI Account Setup

1. Create accounts on both PyPI platforms:
   - **TestPyPI** (for testing): https://test.pypi.org/account/register/
   - **PyPI** (for production): https://pypi.org/account/register/

2. Enable 2FA (Two-Factor Authentication) on both accounts (required for publishing)

3. Create API tokens:
   - Go to Account Settings → API tokens
   - Create a token with "Entire account" scope
   - Save the token securely (you won't see it again!)

### 2. Local Setup

```bash
# Install publishing tools
pip install build twine bump2version

# Install the package in development mode
pip install -e ".[dev]"
```

## Testing the Package Locally

Before publishing, thoroughly test the package:

```bash
# Run all quality checks
make quality

# Build the package
make build

# Check the built package
make check-build
```

## Publishing Process

### Step 1: Test on TestPyPI First

**Always test on TestPyPI before publishing to the real PyPI!**

```bash
# Configure TestPyPI credentials
# Option A: Using .pypirc file
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
EOF

# Option B: Set environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-test-token-here
export TWINE_REPOSITORY=testpypi

# Publish to TestPyPI
make publish-test
```

### Step 2: Test Installation from TestPyPI

```bash
# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-oauth-bridge

# Test that it works
mcp-oauth-bridge --version
mcp-oauth-bridge --help
```

### Step 3: Publish to Production PyPI

**⚠️ WARNING: Publishing to PyPI is permanent! You cannot replace a version once published.**

```bash
# Double-check version number
python -c "import mcp_oauth_bridge; print(mcp_oauth_bridge.__version__)"

# Ensure you're on the main branch and everything is committed
git status
git checkout main
git pull origin main

# Final quality check
make quality

# Publish to PyPI
make publish
```

## Automated Publishing with GitHub Actions

The repository includes GitHub Actions that automatically publish to PyPI when you create a release.

### Setup for Automated Publishing

1. **Configure PyPI Trusted Publishing** (recommended, more secure than API tokens):
   
   a. Go to your PyPI project page
   b. Go to Settings → Publishing
   c. Add a new trusted publisher:
      - Owner: `scottmsilver` (your GitHub username)
      - Repository name: `mcp-oauth-bridge`
      - Workflow name: `ci.yml`
      - Environment name: `pypi`

2. **Create a GitHub Release**:
   ```bash
   # Create and push a tag
   git tag v0.1.0
   git push origin v0.1.0
   
   # Or use the GitHub web interface to create a release
   ```

3. The GitHub Action will automatically:
   - Run tests on multiple Python versions and operating systems
   - Build the package
   - Publish to PyPI if all tests pass

## Version Management

Use semantic versioning (MAJOR.MINOR.PATCH):

```bash
# Bump patch version (0.1.0 → 0.1.1)
make bump-patch

# Bump minor version (0.1.0 → 0.2.0)  
make bump-minor

# Bump major version (0.1.0 → 1.0.0)
make bump-major
```

## Pre-Publication Checklist

Before each release:

- [ ] Update `CHANGELOG.md` with new changes
- [ ] Ensure all tests pass (`make test`)
- [ ] Ensure code quality checks pass (`make quality`)
- [ ] Update documentation if needed
- [ ] Test on TestPyPI first
- [ ] Verify the version number is correct
- [ ] Ensure all dependencies are properly specified
- [ ] Review the built package contents (`twine check dist/*`)

## Post-Publication Steps

After publishing:

1. **Create a GitHub Release**:
   - Go to GitHub → Releases → New Release
   - Tag version: `v0.1.0` (with 'v' prefix)
   - Release title: `Release 0.1.0`
   - Copy changelog entries to release description

2. **Verify PyPI listing**:
   - Check https://pypi.org/project/mcp-oauth-bridge/
   - Ensure README renders correctly
   - Verify all metadata is correct

3. **Test installation**:
   ```bash
   pip install mcp-oauth-bridge
   mcp-oauth-bridge --version
   ```

4. **Announce the release**:
   - Update documentation
   - Post on relevant forums/communities
   - Update any package managers or distributions

## Troubleshooting

### Common Issues

**"File already exists" error**
- You cannot overwrite an existing version on PyPI
- Bump the version number and try again

**"Invalid credentials" error**
- Check your API token is correct
- Ensure 2FA is enabled on your PyPI account
- Try regenerating your API token

**Package not found after publishing**
- PyPI indexing can take a few minutes
- Try again after 5-10 minutes

**README not rendering on PyPI**
- Ensure `long_description_content_type = "text/markdown"` in setup.py
- Check your Markdown syntax is valid

### Getting Help

If you encounter issues:
1. Check the [PyPI documentation](https://packaging.python.org/)
2. Search [existing issues](https://github.com/scottmsilver/mcp-oauth-bridge/issues)
3. Ask on the [Python Packaging Discourse](https://discuss.python.org/c/packaging/14)

## Security Notes

- **Never commit API tokens** to version control
- **Use environment variables** or `.pypirc` for credentials
- **Enable 2FA** on both PyPI and TestPyPI
- **Use trusted publishing** when possible (GitHub Actions)
- **Regularly rotate API tokens**

## Package Maintenance

### Regular Updates

- **Security updates**: Monitor dependencies for vulnerabilities
- **Dependency updates**: Keep dependencies current
- **Python version support**: Add support for new Python versions, drop EOL versions
- **Documentation**: Keep docs current with features

### Monitoring

- **Download statistics**: Check PyPI stats for usage trends
- **Issues**: Monitor GitHub issues for bug reports
- **Dependencies**: Use tools like `pip-audit` to check for vulnerabilities 