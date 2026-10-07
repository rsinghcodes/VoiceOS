"""
LangGraph agent workflow graph builder for VoiceOS.

Implements stateful routing:
  START
    ↓
  classify_intent
    ↓ (conditional routing)
    ├── [human_handoff]   → human_handoff_node   → END
    └── [general/chat]    → response_generator   → END
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agent.state import AgentState
from app.agent.nodes.intent import intent_node
from app.agent.nodes.response import response_node
from app.agent.nodes.handoff import human_handoff_node


def route_after_intent(
    state: AgentState,
) -> Literal["human_handoff", "response_generator"]:
    """
    Evaluate state intent and confidence to decide next step.
    Low confidence (< 0.4) or explicit human_handoff triggers handoff node.
    """
    intent = state.get("intent")
    confidence = state.get("confidence", 1.0)

    if intent == "human_handoff" or (confidence is not None and confidence < 0.4):
        return "human_handoff"

    return "response_generator"


def build_agent_graph(checkpointer=None):
    """
    Build and compile the VoiceOS state graph with optional checkpoint persistence.

    Args:
        checkpointer: LangGraph checkpoint saver (defaults to in-memory MemorySaver).
    """
    builder = StateGraph(AgentState)

    # 1. Register workflow nodes
    builder.add_node("classify_intent", intent_node)
    builder.add_node("human_handoff", human_handoff_node)
    builder.add_node("response_generator", response_node)

    # 2. Wire entry edge
    builder.add_edge(START, "classify_intent")

    # 3. Conditional routing from intent classification
    builder.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "human_handoff": "human_handoff",
            "response_generator": "response_generator",
        },
    )

    # 4. Terminal edges
    builder.add_edge("human_handoff", END)
    builder.add_edge("response_generator", END)

    # Use MemorySaver if no custom checkpointer provided
    cp = checkpointer if checkpointer is not None else MemorySaver()

    return builder.compile(checkpointer=cp)
