"""Agent state definition for LangGraph."""

from typing import Annotated, Any, Dict, List, Literal, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    VoiceOS core agent state — generic, business-agnostic.

    Business-specific data (cart, bookings, etc.) is referenced by ID
    and stored in PostgreSQL, not duplicated here.
    """

    # Voice session
    session_id: str
    business_id: str

    # Customer
    customer_id: Optional[str]

    # Conversation
    messages: Annotated[List[BaseMessage], add_messages]

    # Routing
    intent: Optional[str]
    confidence: Optional[float]

    # Business operation references (IDs only — not full state)
    cart_id: Optional[str]
    order_id: Optional[str]
    booking_id: Optional[str]

    # Tool results from last execution
    tool_results: List[Dict[str, Any]]

    # Workflow control
    workflow_status: Literal[
        "active",
        "awaiting_confirmation",
        "confirmed",
        "completed",
        "human_handoff",
        "error",
    ]

    # Arbitrary metadata for business-specific use
    metadata: Dict[str, Any]
