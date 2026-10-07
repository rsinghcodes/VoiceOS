"""
Google Gemini LLM provider implementation.

Implements LLMInterface using google-genai / langchain-google-genai.
Supports chat and token streaming with tool definitions and fallback handling.
"""

from typing import AsyncIterator, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from app.llm.interface import LLMInterface
from app.config.settings import settings


class GeminiProvider(LLMInterface):
    """
    Concrete LLM provider powered by Google Gemini.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
        temperature: float = 0.2,
    ):
        self.model_name = model_name
        self.api_key = api_key or settings.gemini_api_key
        self.temperature = temperature
        self._client = None

    def _get_client(self):
        """Lazy load langchain-google-genai client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is not configured in settings or environment.")
            from langchain_google_genai import ChatGoogleGenerativeAI
            self._client = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=self.temperature,
            )
        return self._client

    async def chat(
        self,
        messages: List[BaseMessage],
        tools: Optional[list] = None,
    ) -> BaseMessage:
        """Execute chat completion with optional tool definitions."""
        client = self._get_client()
        if tools:
            client = client.bind_tools(tools)
        return await client.ainvoke(messages)

    async def stream_chat(
        self,
        messages: List[BaseMessage],
        tools: Optional[list] = None,
    ) -> AsyncIterator[str]:
        """Stream response tokens for low-latency voice pipeline."""
        client = self._get_client()
        if tools:
            client = client.bind_tools(tools)
        async for chunk in client.astream(messages):
            if chunk.content:
                yield str(chunk.content)
