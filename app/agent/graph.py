"""LangGraph workflow definition for DineVoice assistant."""

from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState


def build_agent_graph():
    """Build and compile the restaurant agent state graph."""
    builder = StateGraph(AgentState)

    # Placeholder entry node
    async def entry_node(state: AgentState) -> dict:
        return state

    builder.add_node("entry", entry_node)
    builder.add_edge(START, "entry")
    builder.add_edge("entry", END)

    return builder.compile()
