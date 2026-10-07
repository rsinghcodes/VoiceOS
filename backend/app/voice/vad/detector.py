"""Voice Activity Detection (VAD) using Silero VAD."""

from typing import Optional
from livekit.plugins import silero


def get_vad(
    min_speech_duration: float = 0.05,
    min_silence_duration: float = 0.5,
    prefix_padding_duration: float = 0.2,
) -> silero.VAD:
    """
    Initialize Silero VAD instance.

    Args:
        min_speech_duration: Minimum speech duration (seconds) to trigger speech start.
        min_silence_duration: Silence duration (seconds) before declaring turn end.
        prefix_padding_duration: Audio prepended to avoid clipping first syllable.
    """
    return silero.VAD.load(
        min_speech_duration=min_speech_duration,
        min_silence_duration=min_silence_duration,
        prefix_padding_duration=prefix_padding_duration,
    )
