from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-oauth-bridge",
    version="0.1.0",
    author="MCP OAuth Bridge Team",
    author_email="team@mcp-oauth-bridge.com",
    description="Local OAuth bridge for MCP servers supporting OpenAI and Anthropic APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/mcp-oauth-bridge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
        "cryptography>=3.4.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "jinja2>=3.0.0",
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.5",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcp-oauth-bridge=mcp_oauth_bridge.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mcp_oauth_bridge": ["templates/*.html"],
    },
) 