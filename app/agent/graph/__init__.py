"""LangGraph agent workflow graph builder."""

from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState


def build_agent_graph():
    """
    Build and compile the VoiceOS agent state graph.

    Node structure (to be expanded per phase):
      START → intent_router → [capability nodes] → response_generator → END
    """
    builder = StateGraph(AgentState)

    # --- Placeholder entry node ---
    async def intent_router(state: AgentState) -> dict:
        """Route based on detected intent to the appropriate capability."""
        return state

    builder.add_node("intent_router", intent_router)
    builder.add_edge(START, "intent_router")
    builder.add_edge("intent_router", END)

    return builder.compile()
