"""
Intent classification node for VoiceOS LangGraph workflow.

Categorizes user input into actionable intents with confidence scores.
"""

from typing import Dict, Any, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from app.agent.state import AgentState


IntentType = Literal[
    "catalog_query",
    "cart_action",
    "order_action",
    "tracking_query",
    "cancellation_query",
    "knowledge_query",
    "human_handoff",
    "confirmation",
    "general_chat",
]


class IntentClassification(BaseModel):
    intent: IntentType = Field(description="Detected high-level user intent")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Brief rationale for this intent classification")


def classify_intent_heuristics(text: str) -> IntentClassification:
    """
    Fast, deterministic intent classifier for common voice patterns.
    Used for instant turn-taking and fallback when LLM is unavailable.
    """
    lower = text.lower().strip()

    # Human handoff
    if any(k in lower for k in ["human", "agent", "manager", "person", "representative", "speak to someone"]):
        return IntentClassification(intent="human_handoff", confidence=0.95, reasoning="Explicit request for human agent")

    # Order tracking
    if any(k in lower for k in ["where is my order", "order status", "track my order", "when will it arrive", "is my food ready"]):
        return IntentClassification(intent="tracking_query", confidence=0.90, reasoning="Inquiry regarding existing order status")

    # Cancellation
    if any(k in lower for k in ["cancel my order", "cancel order", "stop the order"]):
        return IntentClassification(intent="cancellation_query", confidence=0.90, reasoning="Request to cancel an order")

    # Confirmation
    if any(k in lower for k in ["yes", "yeah", "yep", "sure", "confirm", "place it", "go ahead", "do it", "yes please"]):
        return IntentClassification(intent="confirmation", confidence=0.95, reasoning="Direct affirmative confirmation")

    # Cart actions
    if any(k in lower for k in ["add ", "i want ", "give me ", "order two ", "order one ", "remove ", "delete ", "change quantity", "my cart"]):
        return IntentClassification(intent="cart_action", confidence=0.85, reasoning="Adding, updating, or reviewing cart items")

    # Catalog queries
    if any(k in lower for k in ["what pizzas", "what burgers", "what drinks", "do you have", "menu", "show me", "price of", "recommend"]):
        return IntentClassification(intent="catalog_query", confidence=0.85, reasoning="Browsing or querying catalog/menu")

    # Knowledge queries
    if any(k in lower for k in ["open", "hours", "timings", "delivery fee", "delivery time", "allergens", "vegetarian options", "address of restaurant"]):
        return IntentClassification(intent="knowledge_query", confidence=0.85, reasoning="Inquiring about policies, timings, or FAQs")

    return IntentClassification(intent="general_chat", confidence=0.70, reasoning="General conversational input")


async def intent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: analyzes the latest user message and updates intent & confidence in state.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"intent": "general_chat", "confidence": 1.0}

    last_message = messages[-1]
    text = last_message.content if hasattr(last_message, "content") else str(last_message)

    classification = classify_intent_heuristics(text)

    return {
        "intent": classification.intent,
        "confidence": classification.confidence,
    }
