"""
Tool registry and capability-based filtering.

Maps generic tools to required capabilities and dispatches executions
to the active BusinessAdapter with strict Pydantic argument validation.
"""

from typing import Dict, List, Any, Callable, Type
from pydantic import BaseModel, ValidationError
from app.agent.tools.schemas import (
    SearchCatalogInput,
    GetProductInput,
    CheckAvailabilityInput,
    AddToCartInput,
    UpdateCartInput,
    RemoveFromCartInput,
    GetCartInput,
    CalculateTotalInput,
    CreateOrderInput,
    GetOrderStatusInput,
    CancelOrderInput,
    SearchKnowledgeInput,
    TransferToHumanInput,
)
from app.businesses.base.adapter import BusinessAdapter


# Tool specification registry: tool_name -> (required_capability, pydantic_schema, description)
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "search_catalog": {
        "capability": "catalog",
        "schema": SearchCatalogInput,
        "description": "Search the business catalog or menu by natural language query.",
    },
    "get_product": {
        "capability": "catalog",
        "schema": GetProductInput,
        "description": "Get detailed information for a specific catalog item/dish by ID.",
    },
    "check_availability": {
        "capability": "catalog",
        "schema": CheckAvailabilityInput,
        "description": "Check if an item is available in the requested quantity.",
    },
    "add_to_cart": {
        "capability": "cart",
        "schema": AddToCartInput,
        "description": "Add an item with quantity and customizations to the cart.",
    },
    "get_cart": {
        "capability": "cart",
        "schema": GetCartInput,
        "description": "Retrieve current items and subtotal in the cart.",
    },
    "update_cart": {
        "capability": "cart",
        "schema": UpdateCartInput,
        "description": "Update the quantity of an item in the cart.",
    },
    "remove_from_cart": {
        "capability": "cart",
        "schema": RemoveFromCartInput,
        "description": "Remove an item from the cart.",
    },
    "calculate_total": {
        "capability": "cart",
        "schema": CalculateTotalInput,
        "description": "Calculate authoritative subtotal, taxes, delivery fee, and grand total.",
    },
    "create_order": {
        "capability": "ordering",
        "schema": CreateOrderInput,
        "description": "Place a confirmed order with delivery/pickup details (requires customer confirmation).",
    },
    "get_order_status": {
        "capability": "tracking",
        "schema": GetOrderStatusInput,
        "description": "Check the current status and ETA of an existing order.",
    },
    "cancel_order": {
        "capability": "cancellation",
        "schema": CancelOrderInput,
        "description": "Cancel an active order if permitted by business policies.",
    },
    "search_knowledge": {
        "capability": "knowledge",
        "schema": SearchKnowledgeInput,
        "description": "Search business FAQs, policies, operating hours, and general questions.",
    },
    "transfer_to_human": {
        "capability": "core",  # Core is always available
        "schema": TransferToHumanInput,
        "description": "Transfer conversation to a human restaurant staff member.",
    },
}


def get_tools_for_capabilities(capabilities: List[str]) -> List[str]:
    """
    Filter available tool names by active business capabilities.
    Always includes 'core' and 'knowledge' capabilities.
    """
    allowed_caps = set(capabilities) | {"core", "knowledge"}
    return [
        tool_name
        for tool_name, spec in TOOL_REGISTRY.items()
        if spec["capability"] in allowed_caps
    ]


async def execute_tool_call(
    tool_name: str,
    args: Dict[str, Any],
    adapter: BusinessAdapter,
) -> Dict[str, Any]:
    """
    Validate tool arguments with Pydantic and dispatch to BusinessAdapter.

    Returns a structured execution result:
        {"success": bool, "data": Any, "error": Optional[str]}
    """
    if tool_name not in TOOL_REGISTRY:
        return {"success": False, "data": None, "error": f"Unknown tool '{tool_name}'."}

    spec = TOOL_REGISTRY[tool_name]
    schema_cls: Type[BaseModel] = spec["schema"]

    # 1. Deterministic argument validation
    try:
        validated = schema_cls.model_validate(args)
    except ValidationError as e:
        return {
            "success": False,
            "data": None,
            "error": f"Invalid arguments for '{tool_name}': {e.errors()}",
        }

    # 2. Dispatch to BusinessAdapter
    try:
        if tool_name == "search_catalog":
            res = await adapter.search_catalog(query=validated.query)
        elif tool_name == "get_product":
            res = await adapter.get_product(product_id=validated.product_id)
        elif tool_name == "check_availability":
            res = await adapter.check_availability(
                product_id=validated.product_id, quantity=validated.quantity
            )
        elif tool_name == "add_to_cart":
            res = await adapter.add_to_cart(
                cart_id=validated.cart_id,
                product_id=validated.product_id,
                quantity=validated.quantity,
                customizations=validated.customizations,
            )
        elif tool_name == "get_cart":
            res = await adapter.get_cart(cart_id=validated.cart_id)
        elif tool_name == "update_cart":
            res = await adapter.update_cart(
                cart_id=validated.cart_id,
                product_id=validated.product_id,
                quantity=validated.quantity,
            )
        elif tool_name == "remove_from_cart":
            res = await adapter.remove_from_cart(
                cart_id=validated.cart_id,
                product_id=validated.product_id,
            )
        elif tool_name == "calculate_total":
            res = await adapter.calculate_total(cart_id=validated.cart_id)
        elif tool_name == "create_order":
            customer_data = {
                "name": validated.customer_name,
                "phone": validated.phone,
                "delivery_address": validated.delivery_address,
                "order_type": validated.order_type,
                "idempotency_key": validated.idempotency_key,
            }
            res = await adapter.create_transaction(
                cart_id=validated.cart_id,
                customer_data=customer_data,
            )
        elif tool_name == "get_order_status":
            res = await adapter.get_status(transaction_id=validated.order_id)
        elif tool_name == "cancel_order":
            res = await adapter.cancel_transaction(
                transaction_id=validated.order_id, reason=validated.reason
            )
        elif tool_name == "search_knowledge":
            res = await adapter.search_knowledge(query=validated.query)
        elif tool_name == "transfer_to_human":
            res = {
                "status": "transferred",
                "reason": validated.reason,
                "message": "Connecting you to a restaurant representative. Please hold on.",
            }
        else:
            return {"success": False, "data": None, "error": f"Unhandled tool '{tool_name}'"}

        return {"success": True, "data": res, "error": None}

    except Exception as exc:
        return {"success": False, "data": None, "error": str(exc)}
