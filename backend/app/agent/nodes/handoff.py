"""
Human handoff node per VoiceOS BRAIN §36.

Packages customer information, conversation summary, and active session
context into a structured payload for handoff to a human restaurant employee.
"""

from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.agent.state import AgentState


async def human_handoff_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: generates handoff package and returns a soothing voice handover message.
    """
    handoff_reason = state.get("handoff_reason") or "Customer requested human assistance or complex request."
    messages = state.get("messages", [])

    # Assemble summary payload for human agent dashboard
    conversation_summary = [
        f"{m.type}: {m.content}" for m in messages[-6:]
    ]

    handoff_payload = {
        "session_id": state.get("session_id"),
        "business_id": state.get("business_id"),
        "customer_id": state.get("customer_id"),
        "cart_id": state.get("cart_id"),
        "order_id": state.get("order_id"),
        "detected_intent": state.get("intent"),
        "confidence": state.get("confidence"),
        "reason": handoff_reason,
        "recent_dialogue": conversation_summary,
    }

    voice_message = (
        "I'm connecting you to a team member right now. "
        "Please hold the line for just a moment."
    )

    return {
        "workflow_status": "human_handoff",
        "handoff_payload": handoff_payload,
        "messages": [AIMessage(content=voice_message)],
    }
