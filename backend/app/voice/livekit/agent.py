"""LiveKit Voice Pipeline Agent integration with LangGraph agent loop."""

import logging
from typing import Optional, Dict, Any
from livekit.agents import AutoSubscribe, JobContext
from livekit.agents.voice import Agent, AgentSession
from langchain_core.messages import HumanMessage

from app.voice.vad.detector import get_vad
from app.voice.stt.provider import get_stt
from app.voice.tts.provider import get_tts
from app.voice.interruption.handler import InterruptionConfig
from app.agent.graph import build_agent_graph
from app.businesses.restaurant.adapter import RestaurantAdapter
from app.businesses.base.adapter import BusinessAdapter

logger = logging.getLogger("voiceos.livekit")


class VoiceAgentSessionManager:
    """
    Manages session lifecycle and coordinates between LiveKit real-time audio
    and LangGraph conversational/tool workflows.
    """

    def __init__(
        self,
        business_adapter: Optional[BusinessAdapter] = None,
        interruption_config: Optional[InterruptionConfig] = None,
    ):
        self.adapter = business_adapter or RestaurantAdapter()
        self.interruption_config = interruption_config or InterruptionConfig()
        self.graph = build_agent_graph(adapter=self.adapter)
        self.session_states: Dict[str, Dict[str, Any]] = {}

    def get_or_create_state(self, session_id: str, business_id: str = "restaurant_001") -> Dict[str, Any]:
        """Retrieve existing state or initialize standard AgentState."""
        if session_id not in self.session_states:
            self.session_states[session_id] = {
                "session_id": session_id,
                "business_id": business_id,
                "customer_id": None,
                "active_capabilities": self.adapter.get_capabilities(),
                "messages": [],
                "intent": None,
                "confidence": None,
                "cart_id": f"cart_{session_id}",
                "order_id": None,
                "booking_id": None,
                "tool_results": [],
                "retry_count": 0,
                "max_retries": 3,
                "error": None,
                "handoff_reason": None,
                "handoff_payload": None,
                "workflow_status": "active",
                "metadata": {},
            }
        return self.session_states[session_id]

    async def handle_user_speech(self, session_id: str, transcript: str) -> str:
        """
        Processes transcribed speech through LangGraph and produces authoritative voice response text.
        """
        current_state = self.get_or_create_state(session_id)
        current_state["messages"].append(HumanMessage(content=transcript))

        config = {"configurable": {"thread_id": f"thread_{session_id}"}}
        output_state = await self.graph.ainvoke(current_state, config=config)

        # Update cached state
        self.session_states[session_id] = output_state

        # Get latest assistant reply
        messages = output_state.get("messages", [])
        if messages:
            last = messages[-1]
            return last.content if hasattr(last, "content") else str(last)
        return "How can I assist you with your order?"


async def create_voice_agent(
    ctx: JobContext,
    business_name: Optional[str] = None,
    initial_greeting: Optional[str] = None,
    interruption_config: Optional[InterruptionConfig] = None,
    manager: Optional[VoiceAgentSessionManager] = None,
) -> AgentSession:
    """
    Initialize and connect a LiveKit voice AgentSession bound to VoiceAgentSessionManager.
    """
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    session_mgr = manager or VoiceAgentSessionManager(interruption_config=interruption_config)
    cfg = session_mgr.interruption_config
    biz_context = session_mgr.adapter.get_business_context()
    resolved_name = business_name or biz_context.get("name", "Spice Symphony Restaurant")

    vad = get_vad()
    stt = get_stt()
    tts = get_tts()

    # Agent instructions persona
    instructions = (
        f"You are the voice assistant for {resolved_name}. "
        "Keep responses brief (1 to 2 sentences) and conversational. "
        "Never list full menus. Ask clarifying questions one at a time."
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
        or f"Hello! Thanks for calling {resolved_name}. How can I help you today?"
    )

    session.say(greeting, allow_interruptions=True)

    return session
