"""Streaming Speech-to-Text (STT) provider using Deepgram."""

from typing import Optional
from livekit.plugins import deepgram
from app.config.settings import settings


def get_stt(
    language: str = "en",
    model: str = "nova-2",
    api_key: Optional[str] = None,
) -> deepgram.STT:
    """
    Initialize Deepgram streaming STT plugin.

    Args:
        language: BCP-47 language tag (e.g., 'en', 'en-IN').
        model: Deepgram model name ('nova-2' is standard for low-latency voice).
        api_key: Optional Deepgram API key (defaults to settings.deepgram_api_key).
    """
    key = api_key or settings.deepgram_api_key
    return deepgram.STT(
        api_key=key,
        language=language,
        model=model,
    )
