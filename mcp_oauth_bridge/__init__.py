"""
MCP OAuth Bridge - Local OAuth bridge for MCP servers supporting OpenAI and Anthropic APIs

This package provides a local OAuth bridge that eliminates OAuth complexity 
for developers using MCP servers with AI APIs.
"""

__version__ = "0.1.0"
__author__ = "MCP OAuth Bridge Team"

from .config import Config
from .oauth import OAuthHandler
from .proxy import ProxyServer

__all__ = ["Config", "OAuthHandler", "ProxyServer"] 