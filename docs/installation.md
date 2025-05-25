# Installation Guide

## Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection for OAuth flows

## Quick Install

```bash
pip install mcp-oauth-bridge
```

## Installation Options

### 1. From PyPI (Recommended)

```bash
# Install the latest stable version
pip install mcp-oauth-bridge

# Install with development dependencies
pip install mcp-oauth-bridge[dev]

# Install with testing dependencies
pip install mcp-oauth-bridge[test]
```

### 2. From Source

```bash
# Clone the repository
git clone https://github.com/scottmsilver/mcp-oauth-bridge.git
cd mcp-oauth-bridge

# Install in development mode
pip install -e ".[dev]"
```

### 3. Using pipx (Isolated Installation)

```bash
# Install using pipx for global access without affecting system Python
pipx install mcp-oauth-bridge
```

### 4. Using Docker

```bash
# Pull the official Docker image
docker pull mcp-oauth-bridge:latest

# Run with default configuration
docker run -p 3000:3000 -v ~/.mcp-oauth-bridge:/app/config mcp-oauth-bridge:latest
```

## Virtual Environment Setup

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv mcp-oauth-bridge-env

# Activate (Linux/macOS)
source mcp-oauth-bridge-env/bin/activate

# Activate (Windows)
mcp-oauth-bridge-env\Scripts\activate

# Install
pip install mcp-oauth-bridge
```

## Verification

After installation, verify it works:

```bash
# Check version
mcp-oauth-bridge --version

# Run basic test
mcp-oauth-bridge --help
```

## First Time Setup

Initialize the configuration:

```bash
mcp-oauth-bridge init
```

This creates:
- Configuration directory: `~/.mcp-oauth-bridge/`
- Initial config file: `~/.mcp-oauth-bridge/config.yaml`
- Token storage directory: `~/.mcp-oauth-bridge/tokens/`

## Upgrading

```bash
# Upgrade to latest version
pip install --upgrade mcp-oauth-bridge

# Check what changed
mcp-oauth-bridge changelog
```

## Platform-Specific Notes

### macOS

No special requirements. Works on Apple Silicon (M1/M2) and Intel Macs.

### Windows

- Ensure Python is added to PATH
- May need Visual C++ Build Tools for some dependencies

### Linux

Most distributions work out of the box. On minimal installations, you may need:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev build-essential

# CentOS/RHEL/Fedora
sudo yum install python3-devel gcc
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'mcp_oauth_bridge'**
```bash
# Ensure you're in the correct environment
which python
pip list | grep mcp-oauth-bridge
```

**Permission denied errors**
```bash
# Install for user only
pip install --user mcp-oauth-bridge
```

**SSL Certificate errors**
```bash
# Update certificates
pip install --upgrade certifi
```

### Getting Help

If you encounter issues:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Search [existing issues](https://github.com/scottmsilver/mcp-oauth-bridge/issues)
3. Create a [new issue](https://github.com/scottmsilver/mcp-oauth-bridge/issues/new) with:
   - Python version (`python --version`)
   - Operating system
   - Installation method
   - Full error message

## Uninstallation

```bash
# Remove the package
pip uninstall mcp-oauth-bridge

# Remove configuration (optional)
rm -rf ~/.mcp-oauth-bridge/
``` 