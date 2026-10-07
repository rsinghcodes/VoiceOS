"""Barge-in / Interruption handling configuration."""

from dataclasses import dataclass


@dataclass
class InterruptionConfig:
    """
    Configuration for speech interruption and turn detection.

    Attributes:
        allow_interruptions: Whether the user speaking stops current audio playback.
        interrupt_speech_duration: Seconds of speech required before triggering barge-in.
        min_endpointing_delay: Milliseconds of silence after user speech before responding.
    """
    allow_interruptions: bool = True
    interrupt_speech_duration: float = 0.3
    min_endpointing_delay: float = 0.5
