from typing import List, Tuple
from app.agent.state import CartItem


class OrderValidator:
    """Backend deterministic validation for food orders."""

    @staticmethod
    def validate_cart(cart: List[CartItem]) -> Tuple[bool, List[str]]:
        """Verify cart has items and quantities are valid."""
        errors: List[str] = []
        if not cart:
            errors.append("Cart cannot be empty.")
            return False, errors

        for item in cart:
            if item.quantity <= 0:
                errors.append(f"Invalid quantity {item.quantity} for item '{item.name}'.")
            if item.unit_price < 0:
                errors.append(f"Invalid price {item.unit_price} for item '{item.name}'.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_delivery_details(
        order_type: str,
        address: str | None,
        phone: str | None,
    ) -> Tuple[bool, List[str]]:
        """Validate customer delivery details prior to order submission."""
        errors: List[str] = []
        if order_type == "delivery":
            if not address or len(address.strip()) < 5:
                errors.append("A valid delivery address is required for delivery orders.")
        if not phone or len(phone.strip()) < 8:
            errors.append("A valid contact phone number is required.")

        return len(errors) == 0, errors
