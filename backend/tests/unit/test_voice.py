"""Unit tests for Voice Pipeline components: VAD, STT, TTS, Interruption, and VoiceAgentSessionManager."""

import pytest
from app.voice.interruption import InterruptionConfig
from app.voice.vad.detector import get_vad
from app.voice.stt.provider import get_stt
from app.voice.tts.provider import get_tts
from app.voice.livekit.agent import VoiceAgentSessionManager
from app.businesses.restaurant.adapter import RestaurantAdapter


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


def test_vad_instance_creation():
    vad = get_vad(min_speech_duration=0.1, min_silence_duration=0.4)
    assert vad is not None


def test_stt_provider_initialization():
    stt = get_stt(language="en-IN", model="nova-2", api_key="test_dummy_key")
    assert stt is not None


def test_tts_provider_initialization():
    tts = get_tts(model="sonic-english", api_key="test_dummy_key")
    assert tts is not None


@pytest.mark.asyncio
async def test_voice_agent_session_manager_flow():
    adapter = RestaurantAdapter()
    manager = VoiceAgentSessionManager(business_adapter=adapter)

    # 1. State initialized
    session_id = "test_voice_turn_1"
    state = manager.get_or_create_state(session_id)
    assert state["session_id"] == session_id
    assert "catalog" in state["active_capabilities"]

    # 2. Turn 1: User speaks inquiring about chicken dishes
    response = await manager.handle_user_speech(
        session_id=session_id,
        transcript="What chicken dishes do you have?",
    )
    assert isinstance(response, str)
    assert len(response) > 0
    assert any(dish in response for dish in ["Butter Chicken", "Chicken Biryani"])

    # 3. Turn 2: User requests human agent
    response_handoff = await manager.handle_user_speech(
        session_id=session_id,
        transcript="Can I talk to a human agent please?",
    )
    assert "connecting you to a team member" in response_handoff.lower()
