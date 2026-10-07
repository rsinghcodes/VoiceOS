"""LiveKit Voice Pipeline Agent integration."""

import logging
from typing import Optional
from livekit.agents import AutoSubscribe, JobContext
from livekit.agents.voice import Agent, AgentSession
from app.voice.vad.detector import get_vad
from app.voice.stt.provider import get_stt
from app.voice.tts.provider import get_tts
from app.voice.interruption.handler import InterruptionConfig
from app.config.settings import settings

logger = logging.getLogger("voiceos.livekit")


async def create_voice_agent(
    ctx: JobContext,
    business_name: str = "Spice Symphony Restaurant",
    initial_greeting: Optional[str] = None,
    interruption_config: Optional[InterruptionConfig] = None,
) -> AgentSession:
    """
    Initialize and connect a LiveKit voice AgentSession.

    Args:
        ctx: LiveKit worker job context.
        business_name: Name of the business for agent persona.
        initial_greeting: First spoken sentence when user connects.
        interruption_config: Interruption/barge-in settings.
    """
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    cfg = interruption_config or InterruptionConfig()

    vad = get_vad()
    stt = get_stt()
    tts = get_tts()

    # Base instructions for the voice agent persona
    instructions = (
        f"You are the voice assistant for {business_name}. "
        "You are helpful, concise, and speak naturally over the phone. "
        "Keep responses brief (1 to 2 sentences) and conversational. "
        "Never list entire menus unless asked. Ask clarifying questions one at a time."
    )

    agent = Agent(
        instructions=instructions,
        vad=vad,
        stt=stt,
        tts=tts,
        allow_interruptions=cfg.allow_interruptions,
        min_endpointing_delay=cfg.min_endpointing_delay,
    )

    session = AgentSession(
        vad=vad,
        stt=stt,
        tts=tts,
        allow_interruptions=cfg.allow_interruptions,
        min_endpointing_delay=cfg.min_endpointing_delay,
        min_interruption_duration=cfg.interrupt_speech_duration,
    )

    session.start(agent, room=ctx.room)

    greeting = (
        initial_greeting
        or f"Hello! Thanks for calling {business_name}. How can I help you today?"
    )

    await session.say(greeting, allow_interruptions=True)

    return session
