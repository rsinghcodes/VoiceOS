"""
Response generation node for VoiceOS LangGraph workflow.

Synthesizes conversational, brief voice responses based on user messages,
intent, and tool execution results.
"""

from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from app.agent.state import AgentState


def synthesize_voice_response(state: AgentState) -> str:
    """
    Produce a concise, natural voice response based on latest intent and tool outcomes.
    """
    intent = state.get("intent")
    tool_results = state.get("tool_results", [])
    error = state.get("error")

    # If there is an unresolved error
    if error and state.get("workflow_status") == "error":
        return "I'm having trouble processing that request right now. Let me connect you with a team member."

    # Process latest tool results if any
    if tool_results:
        last_tool = tool_results[-1]
        name = last_tool.get("tool")
        data = last_tool.get("data")
        success = last_tool.get("success")

        if not success:
            return "I couldn't complete that action. Could you please repeat or verify what you'd like?"

        if name == "search_catalog":
            if isinstance(data, list) and data:
                items_str = ", ".join(item.get("name", "") for item in data[:3])
                return f"We have {items_str}. Would you like to add any of these to your order?"
            return "I couldn't find matching items in our menu right now. What else would you like?"

        if name == "check_availability":
            available = bool(data)
            return "Yes, that item is freshly available! How many would you like?" if available else "Sorry, that item is currently sold out."

        if name == "add_to_cart":
            return "I've added that to your order. Would you like to add any drinks or sides?"

        if name == "get_cart":
            if isinstance(data, dict):
                items = data.get("items", [])
                subtotal = data.get("subtotal", 0)
                if items:
                    count = len(items)
                    return f"You currently have {count} item{'s' if count > 1 else ''} in your cart, totaling {subtotal} rupees. Would you like to checkout?"
            return "Your cart is currently empty. What would you like to order today?"

        if name == "calculate_total":
            if isinstance(data, dict):
                total = data.get("total", 0)
                return f"Your total comes to {total} rupees including taxes and delivery. Should I place this order for you?"

        if name == "create_order":
            order_id = data.get("order_id", "confirmed") if isinstance(data, dict) else "confirmed"
            return f"Your order #{order_id} has been placed successfully! We're preparing it now."

        if name == "get_order_status":
            status = data.get("status", "in progress") if isinstance(data, dict) else "in progress"
            return f"Your order status is currently {status.lower().replace('_', ' ')}."

        if name == "cancel_order":
            return "Your order has been cancelled as requested."

        if name == "search_knowledge":
            if isinstance(data, list) and data:
                answer = data[0].get("answer", data[0].get("content", ""))
                return answer or "Here is the information you requested."
            return "I couldn't locate that specific information, but our staff will be happy to assist."

    # Intent-based conversational fallbacks
    if intent == "confirmation":
        return "Got it! Proceeding with that now."
    if intent == "catalog_query":
        return "We have delicious pizzas, burgers, combos, and beverages. What are you in the mood for?"
    if intent == "general_chat":
        return "Hello! How can I assist you with your order today?"

    return "How else can I help you with your order today?"


async def response_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node: generates final spoken response and appends AIMessage to conversation history.
    """
    response_text = synthesize_voice_response(state)
    return {
        "messages": [AIMessage(content=response_text)],
    }
