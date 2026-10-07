"""Streaming Text-to-Speech (TTS) provider supporting Sarvam AI and Cartesia."""

from typing import Optional, Any
from app.config.settings import settings


def get_tts(
    provider: Optional[str] = None,
    target_language_code: str = "en-IN",
    model: Optional[str] = None,
    speaker: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Any:
    """
    Initialize streaming TTS plugin based on provider strategy.

    Supported providers:
      - 'sarvam' (default): Sarvam AI Bulbul model (expressive natural voices with sub-250ms latency)
      - 'cartesia': Cartesia streaming TTS
    """
    active_provider = provider or settings.tts_provider.lower()

    if active_provider == "sarvam":
        from livekit.plugins import sarvam
        key = api_key or settings.sarvam_api_key
        tts_model = model or "bulbul:v3"
        return sarvam.TTS(
            api_key=key,
            target_language_code=target_language_code,
            model=tts_model,
            speaker=speaker,
        )

    # Fallback to Cartesia
    from livekit.plugins import cartesia
    key = api_key or settings.cartesia_api_key
    tts_model = model or "sonic-english"
    voice_id = speaker or "248be419-c632-4f23-adf1-5324ed7dbf10"
    return cartesia.TTS(
        api_key=key,
        model=tts_model,
        voice=voice_id,
    )
