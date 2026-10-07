from typing import List, Optional
from app.agent.state import CartItem


class CartManager:
    """Deterministic Cart operations and price calculations."""

    DEFAULT_TAX_RATE = 0.05  # 5% GST/Sales tax
    DEFAULT_DELIVERY_FEE = 40.0  # ₹40 base delivery fee

    @staticmethod
    def add_item(
        cart: List[CartItem],
        item_id: str,
        name: str,
        unit_price: float,
        quantity: int = 1,
        customizations: Optional[List[str]] = None,
    ) -> List[CartItem]:
        """Add an item or increment quantity if identical customizations exist."""
        customizations = customizations or []
        for item in cart:
            if item.item_id == item_id and sorted(item.customizations) == sorted(customizations):
                item.quantity += quantity
                item.item_total = round(item.quantity * item.unit_price, 2)
                return cart

        new_item = CartItem(
            item_id=item_id,
            name=name,
            quantity=quantity,
            unit_price=unit_price,
            customizations=customizations,
            item_total=round(quantity * unit_price, 2),
        )
        cart.append(new_item)
        return cart

    @staticmethod
    def remove_item(cart: List[CartItem], item_id: str) -> List[CartItem]:
        """Remove all instances of an item by item_id."""
        return [item for item in cart if item.item_id != item_id]

    @staticmethod
    def update_quantity(cart: List[CartItem], item_id: str, quantity: int) -> List[CartItem]:
        """Update quantity of an item; removes if quantity <= 0."""
        if quantity <= 0:
            return CartManager.remove_item(cart, item_id)
        for item in cart:
            if item.item_id == item_id:
                item.quantity = quantity
                item.item_total = round(item.quantity * item.unit_price, 2)
                break
        return cart

    @classmethod
    def calculate_totals(
        cls,
        cart: List[CartItem],
        order_type: str = "delivery",
        discount: float = 0.0,
    ) -> dict:
        """Calculate subtotal, tax, delivery fee, and grand total."""
        subtotal = round(sum(item.item_total for item in cart), 2)
        delivery_fee = cls.DEFAULT_DELIVERY_FEE if order_type == "delivery" and subtotal > 0 else 0.0
        taxable_amount = max(0.0, subtotal - discount)
        tax = round(taxable_amount * cls.DEFAULT_TAX_RATE, 2)
        total = round(taxable_amount + tax + delivery_fee, 2)

        return {
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "tax": tax,
            "discount": discount,
            "total": total,
        }
