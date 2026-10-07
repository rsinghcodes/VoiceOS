"""
Tool execution node for VoiceOS LangGraph workflow.

Dispatches validated tool requests to the active BusinessAdapter,
tracks retry attempts, and manages execution errors.
"""

from typing import Dict, Any, List
from app.agent.state import AgentState
from app.agent.tools.registry import execute_tool_call
from app.businesses.base.adapter import BusinessAdapter


async def execute_tools_node(
    state: AgentState,
    adapter: BusinessAdapter,
    pending_tool_calls: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Execute tool calls against the business adapter and update state.

    Args:
        state: Active agent state.
        adapter: Concrete BusinessAdapter for the active business.
        pending_tool_calls: List of dicts: [{"name": str, "args": dict}].
    """
    results: List[Dict[str, Any]] = []
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    error_msg = None

    for call in pending_tool_calls:
        name = call.get("name")
        args = call.get("args", {})

        result = await execute_tool_call(tool_name=name, args=args, adapter=adapter)
        results.append({
            "tool": name,
            "success": result["success"],
            "data": result["data"],
            "error": result["error"],
        })

        if not result["success"]:
            retry_count += 1
            error_msg = result["error"]

    # If retries exceeded, flag error or recommend human handoff
    workflow_status = state.get("workflow_status", "active")
    if retry_count >= max_retries:
        workflow_status = "error"

    return {
        "tool_results": results,
        "retry_count": retry_count,
        "error": error_msg,
        "workflow_status": workflow_status,
    }
