"""
API adapters for different AI platforms

This package contains adapters that translate between different AI API formats
and the MCP protocol, handling the specifics of each platform.
"""

from .openai import OpenAIAdapter
from .anthropic import AnthropicAdapter

__all__ = ["OpenAIAdapter", "AnthropicAdapter"] 