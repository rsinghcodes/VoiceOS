"""
LLM abstraction layer.

The agent is not tied to a single LLM provider.
This package provides a common interface with pluggable provider implementations:
  - Gemini (Google)
  - OpenAI
  - Anthropic
  - Local / Open-source (via vLLM)
"""

from app.llm.interface import LLMInterface

__all__ = ["LLMInterface"]
