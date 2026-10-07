"""Streaming Text-to-Speech (TTS) provider using Cartesia."""

from typing import Optional
from livekit.plugins import cartesia
from app.config.settings import settings


def get_tts(
    model: str = "sonic-english",
    voice: str = "248be419-c632-4f23-adf1-5324ed7dbf10",  # Standard conversational voice
    api_key: Optional[str] = None,
) -> cartesia.TTS:
    """
    Initialize Cartesia streaming TTS plugin.

    Args:
        model: Cartesia model name.
        voice: Voice ID to use for speech synthesis.
        api_key: Optional Cartesia API key (defaults to settings.cartesia_api_key).
    """
    key = api_key or settings.cartesia_api_key
    return cartesia.TTS(
        api_key=key,
        model=model,
        voice=voice,
    )
