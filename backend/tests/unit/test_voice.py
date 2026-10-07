from app.voice.interruption import InterruptionConfig


def test_interruption_config_defaults():
    cfg = InterruptionConfig()
    assert cfg.allow_interruptions is True
    assert cfg.interrupt_speech_duration == 0.3
    assert cfg.min_endpointing_delay == 0.5


def test_interruption_config_custom():
    cfg = InterruptionConfig(
        allow_interruptions=False,
        interrupt_speech_duration=0.5,
        min_endpointing_delay=1.0,
    )
    assert cfg.allow_interruptions is False
    assert cfg.interrupt_speech_duration == 0.5
    assert cfg.min_endpointing_delay == 1.0
