"""Pydantic schemas for agent tool call arguments and validation."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchCatalogInput(BaseModel):
    query: str = Field(description="Search term or food/product description to look up")
    category: Optional[str] = Field(default=None, description="Optional category filter (e.g. 'burgers', 'drinks')")


class GetProductInput(BaseModel):
    product_id: str = Field(description="Unique identifier of the product or dish")


class CheckAvailabilityInput(BaseModel):
    product_id: str = Field(description="Unique identifier of the product or dish")
    quantity: int = Field(default=1, ge=1, description="Quantity to check availability for")


class AddToCartInput(BaseModel):
    cart_id: str = Field(description="Active session cart ID")
    product_id: str = Field(description="Unique identifier of the item to add")
    quantity: int = Field(default=1, ge=1, description="Number of items to add")
    customizations: List[str] = Field(default_factory=list, description="Customization choices, e.g. ['no onions', 'extra cheese']")


class UpdateCartInput(BaseModel):
    cart_id: str = Field(description="Active session cart ID")
    product_id: str = Field(description="Item ID to update")
    quantity: int = Field(ge=0, description="New quantity (0 to remove)")


class RemoveFromCartInput(BaseModel):
    cart_id: str = Field(description="Active session cart ID")
    product_id: str = Field(description="Item ID to remove from cart")


class GetCartInput(BaseModel):
    cart_id: str = Field(description="Active session cart ID to inspect")


class CalculateTotalInput(BaseModel):
    cart_id: str = Field(description="Cart ID to calculate subtotal, taxes, delivery fee, and grand total for")


class CreateOrderInput(BaseModel):
    cart_id: str = Field(description="Cart ID containing confirmed items")
    customer_name: Optional[str] = Field(default=None, description="Customer name")
    phone: Optional[str] = Field(default=None, description="Customer contact phone number")
    delivery_address: Optional[str] = Field(default=None, description="Delivery address if delivery order")
    order_type: str = Field(default="delivery", description="'delivery' or 'pickup'")
    idempotency_key: str = Field(description="Unique idempotency token to prevent duplicate order creation")


class GetOrderStatusInput(BaseModel):
    order_id: str = Field(description="The order ID to check status for")


class CancelOrderInput(BaseModel):
    order_id: str = Field(description="The order ID to cancel")
    reason: Optional[str] = Field(default=None, description="Reason for cancellation")


class SearchKnowledgeInput(BaseModel):
    query: str = Field(description="Question about policies, timings, dietary info, or general FAQs")


class TransferToHumanInput(BaseModel):
    reason: str = Field(description="Why the conversation is being transferred to a human agent")
