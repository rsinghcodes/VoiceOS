"""Agent state definition for LangGraph."""

from typing import Annotated, Any, Dict, List, Literal, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    VoiceOS core agent state — generic, business-agnostic.

    Business-specific data (cart, bookings, etc.) is referenced by ID
    and stored in PostgreSQL/Redis, keeping agent state lean and resilient.
    """

    # Session & multi-tenant identity
    session_id: str
    business_id: str
    customer_id: Optional[str]
    active_capabilities: List[str]

    # Conversation messages (appended via LangGraph add_messages)
    messages: Annotated[List[BaseMessage], add_messages]

    # Intent classification
    intent: Optional[str]
    confidence: Optional[float]

    # References to active operations
    cart_id: Optional[str]
    order_id: Optional[str]
    booking_id: Optional[str]

    # Tool invocation & execution results
    tool_results: List[Dict[str, Any]]

    # Reliability: retry counter for failed operations
    retry_count: int
    max_retries: int
    error: Optional[str]

    # Human handoff
    handoff_reason: Optional[str]
    handoff_payload: Optional[Dict[str, Any]]

    # Workflow lifecycle
    workflow_status: Literal[
        "active",
        "awaiting_confirmation",
        "confirmed",
        "completed",
        "human_handoff",
        "error",
    ]

    # Arbitrary session metadata
    metadata: Dict[str, Any]
