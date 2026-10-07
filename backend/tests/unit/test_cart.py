import pytest
from app.capabilities.cart import CartManager, CartItem


def test_add_item_to_cart():
    cart = []
    cart = CartManager.add_item(
        cart=cart,
        item_id="burger_1",
        name="Chicken Burger",
        unit_price=180.0,
        quantity=2,
        customizations=["No onions"],
    )

    assert len(cart) == 1
    assert cart[0].quantity == 2
    assert cart[0].item_total == 360.0


def test_add_duplicate_item_increments_quantity():
    cart = []
    cart = CartManager.add_item(
        cart=cart,
        item_id="burger_1",
        name="Chicken Burger",
        unit_price=180.0,
        quantity=1,
        customizations=["No onions"],
    )
    cart = CartManager.add_item(
        cart=cart,
        item_id="burger_1",
        name="Chicken Burger",
        unit_price=180.0,
        quantity=2,
        customizations=["No onions"],
    )

    assert len(cart) == 1
    assert cart[0].quantity == 3
    assert cart[0].item_total == 540.0


def test_calculate_totals():
    cart = [
        CartItem(
            item_id="item_1",
            name="Pizza",
            quantity=2,
            unit_price=200.0,
            item_total=400.0,
        )
    ]

    totals = CartManager.calculate_totals(cart, order_type="delivery")
    assert totals["subtotal"] == 400.0
    assert totals["delivery_fee"] == 40.0
    assert totals["tax"] == 20.0  # 5% of 400
    assert totals["total"] == 460.0
