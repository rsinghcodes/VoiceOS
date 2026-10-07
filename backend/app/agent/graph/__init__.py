"""
LangGraph agent workflow graph builder for VoiceOS.

Implements stateful routing with business adapter tool invocation:
  START
    ↓
  classify_intent
    ↓ (conditional routing)
    ├── [human_handoff]        → human_handoff_node → END
    ├── [tool_action]          → execute_tools      → response_generator → END
    └── [general_chat]         → response_generator → END
"""

from typing import Literal, Optional, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import AgentState
from app.agent.nodes.intent import intent_node
from app.agent.nodes.response import response_node
from app.agent.nodes.handoff import human_handoff_node
from app.agent.nodes.tool_node import execute_tools_node
from app.businesses.base.adapter import BusinessAdapter


TOOL_INTENTS = {
    "catalog_query",
    "cart_action",
    "order_action",
    "tracking_query",
    "cancellation_query",
    "knowledge_query",
}


def route_after_intent(
    state: AgentState,
) -> Literal["human_handoff", "execute_tools", "response_generator"]:
    """
    Evaluate state intent, confidence, and pending tools to decide next step:
      1. Low confidence (< 0.4) or explicit human_handoff -> human_handoff
      2. Intents requiring business actions or pending tools -> execute_tools
      3. Otherwise -> direct response_generator
    """
    intent = state.get("intent")
    confidence = state.get("confidence", 1.0)

    if intent == "human_handoff" or (confidence is not None and confidence < 0.4):
        return "human_handoff"

    # If the user has a tool-oriented intent or explicit pending calls in metadata
    pending = state.get("metadata", {}).get("pending_tools", [])
    if pending or (intent in TOOL_INTENTS):
        return "execute_tools"

    return "response_generator"


def build_agent_graph(
    adapter: Optional[BusinessAdapter] = None,
    checkpointer=None,
):
    """
    Build and compile the VoiceOS state graph with tool execution and optional checkpoint persistence.

    Args:
        adapter: Concrete BusinessAdapter instance for executing actions (e.g. RestaurantAdapter).
        checkpointer: LangGraph checkpoint saver (defaults to MemorySaver).
    """
    builder = StateGraph(AgentState)

    # Wrap tool execution node with the bound adapter
    async def _tool_node_runner(state: AgentState):
        if not adapter:
            return {"tool_results": []}

        # Resolve pending tools from metadata or synthesize from intent
        pending = state.get("metadata", {}).get("pending_tools", [])
        intent = state.get("intent")

        if not pending and intent == "catalog_query":
            # Extract last message query
            msgs = state.get("messages", [])
            query = msgs[-1].content if msgs else ""
            pending = [{"name": "search_catalog", "args": {"query": str(query)}}]

        elif not pending and intent == "tracking_query":
            order_id = state.get("order_id", "latest")
            pending = [{"name": "get_order_status", "args": {"order_id": order_id}}]

        elif not pending and intent == "knowledge_query":
            msgs = state.get("messages", [])
            query = msgs[-1].content if msgs else ""
            pending = [{"name": "search_knowledge", "args": {"query": str(query)}}]

        res = await execute_tools_node(
            state=state,
            adapter=adapter,
            pending_tool_calls=pending,
        )
        return res

    # 1. Register workflow nodes
    builder.add_node("classify_intent", intent_node)
    builder.add_node("human_handoff", human_handoff_node)
    builder.add_node("execute_tools", _tool_node_runner)
    builder.add_node("response_generator", response_node)

    # 2. Wire entry edge
    builder.add_edge(START, "classify_intent")

    # 3. Conditional routing from intent classification
    builder.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "human_handoff": "human_handoff",
            "execute_tools": "execute_tools",
            "response_generator": "response_generator",
        },
    )

    # 4. Chain tool executions to response generator
    builder.add_edge("execute_tools", "response_generator")

    # 5. Terminal edges
    builder.add_edge("human_handoff", END)
    builder.add_edge("response_generator", END)

    # Use MemorySaver if no custom checkpointer provided
    cp = checkpointer if checkpointer is not None else MemorySaver()

    return builder.compile(checkpointer=cp)
