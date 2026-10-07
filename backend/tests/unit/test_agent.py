import pytest
from langchain_core.messages import HumanMessage
from app.agent.nodes.intent import classify_intent_heuristics
from app.agent.prompts.builder import build_system_prompt
from app.agent.tools.registry import get_tools_for_capabilities, execute_tool_call
from app.agent.nodes.tool_node import execute_tools_node
from app.agent.graph import build_agent_graph
from tests.mocks.mock_adapter import MockBusinessAdapter


def test_intent_classification():
    assert classify_intent_heuristics("I want to speak to a person").intent == "human_handoff"
    assert classify_intent_heuristics("Where is my order?").intent == "tracking_query"
    assert classify_intent_heuristics("Cancel my order please").intent == "cancellation_query"
    assert classify_intent_heuristics("Yes, confirm it").intent == "confirmation"
    assert classify_intent_heuristics("Add two chicken burgers").intent == "cart_action"
    assert classify_intent_heuristics("What pizzas do you have?").intent == "catalog_query"
    assert classify_intent_heuristics("What are your opening hours?").intent == "knowledge_query"
    assert classify_intent_heuristics("Hello there").intent == "general_chat"


def test_layered_prompt_builder():
    prompt = build_system_prompt(
        business_context={"name": "Spice Symphony", "type": "restaurant"},
        active_capabilities=["catalog", "cart", "ordering"],
        policies={"require_order_confirmation": True, "min_order_amount": 150.0},
    )
    assert "Spice Symphony" in prompt
    assert "NEVER guess, estimate, or make up prices" in prompt
    assert "Catalog instructions:" in prompt
    assert "Ordering instructions:" in prompt
    assert "Minimum order value is 150.0" in prompt


def test_capability_tool_filtering():
    # Business with only catalog capability
    tools_catalog_only = get_tools_for_capabilities(["catalog"])
    assert "search_catalog" in tools_catalog_only
    assert "get_product" in tools_catalog_only
    assert "add_to_cart" not in tools_catalog_only
    assert "create_order" not in tools_catalog_only
    assert "transfer_to_human" in tools_catalog_only  # Core is always included

    # Business with full restaurant capabilities
    tools_full = get_tools_for_capabilities(["catalog", "cart", "ordering", "tracking", "cancellation"])
    assert "add_to_cart" in tools_full
    assert "create_order" in tools_full
    assert "get_order_status" in tools_full
    assert "cancel_order" in tools_full


@pytest.mark.asyncio
async def test_tool_execution_and_validation():
    adapter = MockBusinessAdapter()

    # 1. Successful search_catalog
    res = await execute_tool_call(
        tool_name="search_catalog",
        args={"query": "Burger"},
        adapter=adapter,
    )
    assert res["success"] is True
    assert len(res["data"]) == 1
    assert res["data"][0]["name"] == "Chicken Burger"

    # 2. Argument validation error (missing required product_id in check_availability)
    bad_res = await execute_tool_call(
        tool_name="check_availability",
        args={},  # Missing product_id
        adapter=adapter,
    )
    assert bad_res["success"] is False
    assert "Invalid arguments" in bad_res["error"]


@pytest.mark.asyncio
async def test_tool_node_retry_handling():
    adapter = MockBusinessAdapter()
    adapter.should_fail = True  # Simulate backend failure

    state = {
        "session_id": "sess_1",
        "business_id": "restaurant_001",
        "retry_count": 0,
        "max_retries": 2,
        "workflow_status": "active",
    }

    result_state = await execute_tools_node(
        state=state,
        adapter=adapter,
        pending_tool_calls=[{"name": "search_catalog", "args": {"query": "Pizza"}}],
    )

    assert result_state["retry_count"] == 1
    assert result_state["tool_results"][0]["success"] is False
    assert result_state["error"] is not None


@pytest.mark.asyncio
async def test_agent_graph_execution():
    graph = build_agent_graph()

    # Turn 1: General menu inquiry
    initial_state = {
        "session_id": "test_sess_001",
        "business_id": "restaurant_001",
        "customer_id": None,
        "active_capabilities": ["catalog", "cart", "ordering"],
        "messages": [HumanMessage(content="What pizzas do you have?")],
        "intent": None,
        "confidence": None,
        "cart_id": None,
        "order_id": None,
        "booking_id": None,
        "tool_results": [],
        "retry_count": 0,
        "max_retries": 3,
        "error": None,
        "handoff_reason": None,
        "handoff_payload": None,
        "workflow_status": "active",
        "metadata": {},
    }

    config = {"configurable": {"thread_id": "thread_1"}}
    output = await graph.ainvoke(initial_state, config=config)

    assert output["intent"] == "catalog_query"
    assert output["workflow_status"] == "active"
    assert len(output["messages"]) >= 2
    assert "pizza" in output["messages"][-1].content.lower()


@pytest.mark.asyncio
async def test_agent_graph_human_handoff_routing():
    graph = build_agent_graph()

    # User asks for human
    handoff_state = {
        "session_id": "test_sess_002",
        "business_id": "restaurant_001",
        "customer_id": "cust_123",
        "active_capabilities": ["catalog"],
        "messages": [HumanMessage(content="I want to speak to a person right now")],
        "intent": None,
        "confidence": None,
        "cart_id": None,
        "order_id": None,
        "booking_id": None,
        "tool_results": [],
        "retry_count": 0,
        "max_retries": 3,
        "error": None,
        "handoff_reason": None,
        "handoff_payload": None,
        "workflow_status": "active",
        "metadata": {},
    }

    config = {"configurable": {"thread_id": "thread_2"}}
    output = await graph.ainvoke(handoff_state, config=config)

    assert output["intent"] == "human_handoff"
    assert output["workflow_status"] == "human_handoff"
    assert output["handoff_payload"] is not None
    assert output["handoff_payload"]["customer_id"] == "cust_123"
    assert "connecting you to a team member" in output["messages"][-1].content.lower()


@pytest.mark.asyncio
async def test_agent_graph_tool_loop_with_restaurant_adapter():
    from app.businesses.restaurant.adapter import RestaurantAdapter

    adapter = RestaurantAdapter()
    graph = build_agent_graph(adapter=adapter)

    # User asks what pizzas they have -> routes to execute_tools -> search_catalog -> response_generator
    state = {
        "session_id": "test_sess_tool_loop",
        "business_id": "restaurant_001",
        "customer_id": None,
        "active_capabilities": ["catalog", "cart", "ordering"],
        "messages": [HumanMessage(content="What chicken dishes do you have?")],
        "intent": None,
        "confidence": None,
        "cart_id": None,
        "order_id": None,
        "booking_id": None,
        "tool_results": [],
        "retry_count": 0,
        "max_retries": 3,
        "error": None,
        "handoff_reason": None,
        "handoff_payload": None,
        "workflow_status": "active",
        "metadata": {},
    }

    config = {"configurable": {"thread_id": "thread_tool_loop"}}
    output = await graph.ainvoke(state, config=config)

    assert output["intent"] == "catalog_query"
    assert len(output["tool_results"]) >= 1
    assert output["tool_results"][0]["tool"] == "search_catalog"
    assert output["tool_results"][0]["success"] is True
    # Verify spoken response was synthesized from tool data
    last_msg = output["messages"][-1].content
    assert any(dish in last_msg for dish in ["Butter Chicken", "Chicken Biryani"])
