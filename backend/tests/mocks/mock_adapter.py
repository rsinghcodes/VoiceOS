"""Mock BusinessAdapter for testing agent workflows and tool executions."""

from typing import Any, Dict, List, Optional
from app.businesses.base.adapter import BusinessAdapter


class MockBusinessAdapter(BusinessAdapter):
    """In-memory business adapter for tests."""

    def __init__(self, business_id: str = "restaurant_001"):
        self.business_id = business_id
        self.catalog = [
            {"id": "dish_1", "name": "Chicken Burger", "price": 180.0, "available": True},
            {"id": "dish_2", "name": "Veggie Pizza", "price": 250.0, "available": True},
            {"id": "dish_3", "name": "French Fries", "price": 90.0, "available": True},
        ]
        self.carts: Dict[str, Dict[str, Any]] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.should_fail = False

    async def search_catalog(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        if self.should_fail:
            raise RuntimeError("Catalog service temporarily unavailable")
        q = query.lower()
        return [item for item in self.catalog if q in item["name"].lower()]

    async def get_product(self, product_id: str) -> Optional[Dict]:
        for item in self.catalog:
            if item["id"] == product_id:
                return item
        return None

    async def check_availability(self, product_id: str, quantity: int = 1) -> bool:
        prod = await self.get_product(product_id)
        return bool(prod and prod.get("available", False))

    async def create_cart(self, session_id: str, customer_id: Optional[str] = None) -> str:
        cart_id = f"cart_{session_id}"
        self.carts[cart_id] = {"items": [], "subtotal": 0.0}
        return cart_id

    async def get_cart(self, cart_id: str) -> Dict:
        return self.carts.get(cart_id, {"items": [], "subtotal": 0.0})

    async def add_to_cart(
        self,
        cart_id: str,
        product_id: str,
        quantity: int,
        customizations: Optional[List[str]] = None,
    ) -> Dict:
        if cart_id not in self.carts:
            self.carts[cart_id] = {"items": [], "subtotal": 0.0}
        prod = await self.get_product(product_id)
        price = prod["price"] if prod else 100.0
        item = {
            "product_id": product_id,
            "name": prod["name"] if prod else "Custom Item",
            "quantity": quantity,
            "price": price,
            "customizations": customizations or [],
        }
        self.carts[cart_id]["items"].append(item)
        self.carts[cart_id]["subtotal"] += price * quantity
        return self.carts[cart_id]

    async def update_cart(self, cart_id: str, product_id: str, quantity: int) -> Dict:
        cart = self.carts.get(cart_id, {"items": [], "subtotal": 0.0})
        cart["items"] = [i for i in cart["items"] if i["product_id"] != product_id]
        if quantity > 0:
            prod = await self.get_product(product_id)
            price = prod["price"] if prod else 100.0
            cart["items"].append({"product_id": product_id, "quantity": quantity, "price": price})
        return cart

    async def remove_from_cart(self, cart_id: str, product_id: str) -> Dict:
        return await self.update_cart(cart_id, product_id, 0)

    async def calculate_total(self, cart_id: str) -> Dict:
        cart = await self.get_cart(cart_id)
        subtotal = cart.get("subtotal", 0.0)
        tax = round(subtotal * 0.05, 2)
        delivery_fee = 40.0 if subtotal > 0 else 0.0
        total = round(subtotal + tax + delivery_fee, 2)
        return {"subtotal": subtotal, "tax": tax, "delivery_fee": delivery_fee, "total": total}

    async def create_transaction(self, cart_id: str, customer_data: Dict) -> Dict:
        totals = await self.calculate_total(cart_id)
        order_id = f"ord_{len(self.orders) + 1001}"
        order = {
            "order_id": order_id,
            "status": "CONFIRMED",
            "cart_id": cart_id,
            "customer": customer_data,
            "total": totals["total"],
        }
        self.orders[order_id] = order
        return order

    async def get_status(self, transaction_id: str) -> Dict:
        order = self.orders.get(transaction_id)
        if order:
            return {"order_id": transaction_id, "status": order["status"]}
        return {"order_id": transaction_id, "status": "PREPARING"}

    async def cancel_transaction(self, transaction_id: str, reason: Optional[str] = None) -> Dict:
        if transaction_id in self.orders:
            self.orders[transaction_id]["status"] = "CANCELLED"
        return {"order_id": transaction_id, "status": "CANCELLED", "reason": reason}

    async def search_knowledge(self, query: str) -> List[Dict]:
        return [{"answer": "We are open daily from 11 AM to 11 PM."}]

    def get_capabilities(self) -> List[str]:
        return ["catalog", "cart", "ordering", "tracking", "cancellation"]

    def get_business_context(self) -> Dict[str, Any]:
        return {"name": "Spice Symphony", "type": "restaurant"}
