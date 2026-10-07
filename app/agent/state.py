from typing import Annotated, List, Optional, Dict, Any, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class CustomerInfo(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class CartItem(BaseModel):
    item_id: str
    name: str
    quantity: int = 1
    unit_price: float = 0.0
    customizations: List[str] = Field(default_factory=list)
    item_total: float = 0.0


class AgentState(TypedDict):
    """LangGraph conversation and ordering state."""
    messages: Annotated[List[BaseMessage], add_messages]
    customer: CustomerInfo
    order_type: Literal["delivery", "pickup", "unspecified"]
    cart: List[CartItem]
    delivery_address: Optional[str]
    subtotal: float
    delivery_fee: float
    tax: float
    discount: float
    total: float
    order_status: Literal[
        "browsing",
        "configuring_cart",
        "awaiting_address",
        "awaiting_confirmation",
        "confirmed",
        "cancelled",
        "transferred_to_human",
    ]
    current_intent: Optional[str]
    metadata: Dict[str, Any]
