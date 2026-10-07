"""Streaming Speech-to-Text (STT) provider supporting Sarvam AI and Deepgram."""

from typing import Optional, Any
from app.config.settings import settings


def get_stt(
    provider: Optional[str] = None,
    language: str = "en-IN",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Any:
    """
    Initialize streaming STT plugin based on provider strategy.

    Supported providers:
      - 'sarvam' (default): Sarvam AI Saaras model (optimized for Indian English, Hindi, and regional languages)
      - 'deepgram': Deepgram Nova-2 streaming STT
    """
    active_provider = provider or settings.stt_provider.lower()

    if active_provider == "sarvam":
        from livekit.plugins import sarvam
        key = api_key or settings.sarvam_api_key
        stt_model = model or "saaras:v4"
        return sarvam.STT(
            api_key=key,
            language=language,
            model=stt_model,
        )

    # Fallback to Deepgram
    from livekit.plugins import deepgram
    key = api_key or settings.deepgram_api_key
    stt_model = model or "nova-2"
    return deepgram.STT(
        api_key=key,
        language=language,
        model=stt_model,
    )
