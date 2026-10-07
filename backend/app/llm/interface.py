"""LLM provider interface — Strategy pattern for pluggable LLM backends."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List
from langchain_core.messages import BaseMessage


class LLMInterface(ABC):
    """
    Abstract base for all LLM providers.

    The agent interacts with this interface only.
    Swap providers by changing the concrete implementation.
    """

    @abstractmethod
    async def chat(
        self,
        messages: List[BaseMessage],
        tools: list | None = None,
    ) -> BaseMessage:
        """Send a chat request and return the full response."""
        ...

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[BaseMessage],
        tools: list | None = None,
    ) -> AsyncIterator[str]:
        """Stream a chat response token by token."""
        ...
