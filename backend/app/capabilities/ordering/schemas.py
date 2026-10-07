from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.capabilities.cart.schemas import CartItem


class CustomerInfo(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class OrderStatus(str, Enum):
    CART = "CART"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    READY = "READY"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderCreateRequest(BaseModel):
    customer: CustomerInfo
    order_type: str = "delivery"
    delivery_address: Optional[str] = None
    cart: List[CartItem]
    subtotal: float
    delivery_fee: float
    tax: float
    discount: float = 0.0
    total: float
    payment_method: str = "cash_on_delivery"


class OrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    customer: CustomerInfo
    order_type: str
    items: List[CartItem]
    total: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
