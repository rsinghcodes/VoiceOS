from typing import List, Optional
from pydantic import BaseModel, Field


class CartItem(BaseModel):
    item_id: str
    name: str
    quantity: int = 1
    unit_price: float = 0.0
    customizations: List[str] = Field(default_factory=list)
    item_total: float = 0.0
