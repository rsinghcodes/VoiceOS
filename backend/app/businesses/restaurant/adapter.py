"""
Restaurant business adapter implementation for Spice Symphony (restaurant_001).

Implements BusinessAdapter protocol, binding generic agent actions to
PostgreSQL repositories, deterministic cart calculation, and local business config.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from app.businesses.base.adapter import BusinessAdapter
from app.capabilities.cart.manager import CartManager
from app.capabilities.cart.schemas import CartItem
from app.database.models.models import OrderType, OrderStatus
from app.database.repositories.repositories import CatalogRepository, OrderRepository


class RestaurantAdapter(BusinessAdapter):
    """
    Concrete adapter for restaurant food ordering.

    Loads restaurant business configuration (e.g. policies, tax rates, delivery fees)
    and executes catalog searches, cart operations, and orders against database repositories.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        catalog_repo: Optional[CatalogRepository] = None,
        order_repo: Optional[OrderRepository] = None,
        knowledge_retriever: Optional[Any] = None,
    ):
        self.catalog_repo = catalog_repo
        self.order_repo = order_repo
        self.knowledge_retriever = knowledge_retriever
        self.carts: Dict[str, List[CartItem]] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}  # In-memory fallback if order_repo is None

        # Load business config
        if config_path is None:
            # Default to restaurant_001
            base_dir = Path(__file__).resolve().parents[3]
            config_path = str(base_dir / "businesses" / "restaurant_001" / "config.yaml")

        self.config = self._load_config(config_path)
        self.business_id = self.config.get("business", {}).get("id", "restaurant_001")
        self.business_name = self.config.get("business", {}).get("name", "Spice Symphony Restaurant")
        self.policies = self.config.get("policies", {})
        self.capabilities = self.config.get("capabilities", [
            "catalog", "cart", "ordering", "delivery", "pickup", "tracking", "cancellation"
        ])

        # Preloaded static knowledge base fallback
        self.knowledge = [
            {"query": "hours", "answer": f"{self.business_name} is open every day from 11:00 AM to 11:00 PM."},
            {"query": "delivery", "answer": f"Standard delivery takes 30-40 minutes with a fee of ₹{self.policies.get('delivery_fee', 40.0)}."},
            {"query": "cancellation", "answer": f"Orders can be cancelled within {self.policies.get('cancellation_window_minutes', 5)} minutes of placement."},
            {"query": "min_order", "answer": f"Minimum order amount is ₹{self.policies.get('min_order_amount', 150.0)}."},
        ]

    def _load_config(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    # ---- Catalog ----

    async def search_catalog(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search products via CatalogRepository or static fallback."""
        if self.catalog_repo:
            products = await self.catalog_repo.search_products(
                business_id=self.business_id, query=query
            )
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "is_available": p.is_available,
                    "tags": p.tags or [],
                }
                for p in products
            ]

        # In-memory menu fallback if repository not supplied
        default_menu = [
            {"id": "dish_1", "name": "Butter Chicken", "price": 320.0, "is_available": True, "tags": ["non-veg", "curry"]},
            {"id": "dish_2", "name": "Paneer Tikka", "price": 240.0, "is_available": True, "tags": ["veg", "starter"]},
            {"id": "dish_3", "name": "Garlic Naan", "price": 50.0, "is_available": True, "tags": ["veg", "bread"]},
            {"id": "dish_4", "name": "Chicken Biryani", "price": 280.0, "is_available": True, "tags": ["non-veg", "rice"]},
            {"id": "dish_5", "name": "Mango Lassi", "price": 80.0, "is_available": True, "tags": ["veg", "beverage"]},
        ]
        q = query.lower().strip()
        tokens = [w for w in q.split() if len(w) > 2 and w not in ["what", "have", "dishes", "food", "show", "items"]]
        if not tokens:
            return default_menu
        return [
            item for item in default_menu
            if q in item["name"].lower()
            or any(t in item["name"].lower() for t in tokens)
            or any(t in tag for t in tokens for tag in item["tags"])
        ]

    async def get_product(self, product_id: str) -> Optional[Dict]:
        if self.catalog_repo:
            p = await self.catalog_repo.get_product_by_id(self.business_id, product_id)
            if p:
                return {"id": p.id, "name": p.name, "price": p.price, "is_available": p.is_available}
            return None

        for item in await self.search_catalog(""):
            if item["id"] == product_id:
                return item
        return None

    async def check_availability(self, product_id: str, quantity: int = 1) -> bool:
        if self.catalog_repo:
            return await self.catalog_repo.check_availability(self.business_id, product_id, quantity)

        prod = await self.get_product(product_id)
        return bool(prod and prod.get("is_available", False))

    # ---- Cart / Session ----

    async def create_cart(self, session_id: str, customer_id: Optional[str] = None) -> str:
        cart_id = f"cart_{session_id}"
        self.carts[cart_id] = []
        return cart_id

    async def get_cart(self, cart_id: str) -> Dict:
        items = self.carts.get(cart_id, [])
        totals = await self.calculate_total(cart_id)
        return {
            "cart_id": cart_id,
            "items": [item.model_dump() for item in items],
            "subtotal": totals["subtotal"],
            "total": totals["total"],
        }

    async def add_to_cart(
        self,
        cart_id: str,
        product_id: str,
        quantity: int,
        customizations: Optional[List[str]] = None,
    ) -> Dict:
        if cart_id not in self.carts:
            self.carts[cart_id] = []

        prod = await self.get_product(product_id)
        name = prod["name"] if prod else "Special Dish"
        price = prod["price"] if prod else 100.0

        CartManager.add_item(
            cart=self.carts[cart_id],
            item_id=product_id,
            name=name,
            unit_price=price,
            quantity=quantity,
            customizations=customizations,
        )
        return await self.get_cart(cart_id)

    async def update_cart(self, cart_id: str, product_id: str, quantity: int) -> Dict:
        if cart_id in self.carts:
            CartManager.update_quantity(self.carts[cart_id], product_id, quantity)
        return await self.get_cart(cart_id)

    async def remove_from_cart(self, cart_id: str, product_id: str) -> Dict:
        if cart_id in self.carts:
            CartManager.remove_item(self.carts[cart_id], product_id)
        return await self.get_cart(cart_id)

    async def calculate_total(self, cart_id: str) -> Dict:
        items = self.carts.get(cart_id, [])
        delivery_fee = float(self.policies.get("delivery_fee", 40.0))
        tax_rate = float(self.policies.get("tax_rate", 0.05))

        subtotal = round(sum(item.item_total for item in items), 2)
        fee = delivery_fee if subtotal > 0 else 0.0
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + fee + tax, 2)

        return {
            "subtotal": subtotal,
            "delivery_fee": fee,
            "tax": tax,
            "total": total,
        }

    # ---- Transaction ----

    async def create_transaction(self, cart_id: str, customer_data: Dict) -> Dict:
        cart_items = self.carts.get(cart_id, [])
        if not cart_items:
            raise ValueError("Cannot create order from an empty cart.")

        totals = await self.calculate_total(cart_id)

        # Enforce minimum order policy
        min_order = float(self.policies.get("min_order_amount", 0.0))
        if totals["subtotal"] < min_order:
            raise ValueError(f"Minimum order subtotal must be at least ₹{min_order}.")

        order_type_str = customer_data.get("order_type", "delivery").upper()
        order_type = OrderType.PICKUP if order_type_str == "PICKUP" else OrderType.DELIVERY
        idempotency_key = customer_data.get("idempotency_key")

        if self.order_repo:
            items_payload = [
                {
                    "product_id": item.item_id,
                    "name": item.name,
                    "price": item.unit_price,
                    "quantity": item.quantity,
                    "customizations": item.customizations,
                }
                for item in cart_items
            ]
            db_order = await self.order_repo.create_order(
                business_id=self.business_id,
                customer_id=customer_data.get("customer_id"),
                session_id=customer_data.get("session_id"),
                idempotency_key=idempotency_key,
                order_type=order_type,
                items=items_payload,
                subtotal=totals["subtotal"],
                tax=totals["tax"],
                delivery_fee=totals["delivery_fee"],
                total=totals["total"],
                delivery_address=customer_data.get("delivery_address"),
            )
            # Empty cart after successful placement
            self.carts[cart_id] = []
            return {
                "order_id": db_order.id,
                "status": db_order.status.value,
                "total": db_order.total,
                "order_type": db_order.order_type.value,
                "customer": customer_data,
            }

        # In-memory fallback
        import uuid
        order_id = f"ord_{uuid.uuid4().hex[:8]}"
        order_record = {
            "order_id": order_id,
            "status": "CONFIRMED",
            "total": totals["total"],
            "order_type": order_type_str,
            "customer": customer_data,
        }
        self.orders[order_id] = order_record
        self.carts[cart_id] = []
        return order_record

    async def get_status(self, transaction_id: str) -> Dict:
        if self.order_repo:
            order = await self.order_repo.get_order_by_id(self.business_id, transaction_id)
            if order:
                return {"order_id": order.id, "status": order.status.value, "total": order.total}

        if transaction_id in self.orders:
            o = self.orders[transaction_id]
            return {"order_id": transaction_id, "status": o["status"], "total": o["total"]}

        return {"order_id": transaction_id, "status": "CONFIRMED"}

    async def cancel_transaction(self, transaction_id: str, reason: Optional[str] = None) -> Dict:
        if self.order_repo:
            order = await self.order_repo.update_status(
                self.business_id, transaction_id, OrderStatus.CANCELLED, reason
            )
            if order:
                return {"order_id": order.id, "status": order.status.value, "reason": reason}

        if transaction_id in self.orders:
            self.orders[transaction_id]["status"] = "CANCELLED"
            self.orders[transaction_id]["reason"] = reason

        return {"order_id": transaction_id, "status": "CANCELLED", "reason": reason}

    # ---- Knowledge ----
 
    async def search_knowledge(self, query: str) -> List[Dict]:
        if self.knowledge_retriever:
            docs = await self.knowledge_retriever.retrieve(
                business_id=self.business_id,
                query=query,
                top_k=2,
            )
            if docs:
                return [{"answer": d["text"], "score": d.get("score")} for d in docs]

        q = query.lower()
        matches = [k for k in self.knowledge if k["query"] in q]
        return matches or [{"answer": f"For assistance with {self.business_name}, please speak with our host."}]

    # ---- Metadata ----

    def get_capabilities(self) -> List[str]:
        return self.capabilities

    def get_business_context(self) -> Dict[str, Any]:
        return {
            "id": self.business_id,
            "name": self.business_name,
            "type": "restaurant",
            "policies": self.policies,
        }
