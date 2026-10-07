"""Catalog and Order repository access functions."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.models import (
    Business,
    Category,
    Product,
    Customer,
    Order,
    OrderItem,
    OrderStatus,
    OrderType,
)


class CatalogRepository:
    """Read & search repository for multi-tenant business catalogs."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_products(
        self,
        business_id: str,
        query: str,
        category_id: Optional[str] = None,
        available_only: bool = True,
    ) -> List[Product]:
        """Search products by name or description with multi-tenant scoping."""
        stmt = select(Product).where(Product.business_id == business_id)

        if available_only:
            stmt = stmt.where(Product.is_available.is_(True))

        if category_id:
            stmt = stmt.where(Product.category_id == category_id)

        if query:
            pattern = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern),
                )
            )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_product_by_id(self, business_id: str, product_id: str) -> Optional[Product]:
        """Retrieve single product by ID ensuring business tenancy."""
        stmt = select(Product).where(
            Product.business_id == business_id,
            Product.id == product_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def check_availability(self, business_id: str, product_id: str, quantity: int = 1) -> bool:
        """Deterministic availability check."""
        product = await self.get_product_by_id(business_id, product_id)
        if not product or not product.is_available:
            return False
        if product.inventory_count is not None and product.inventory_count < quantity:
            return False
        return True


class OrderRepository:
    """Authoritative repository for transactional order management with idempotency."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_order_by_idempotency_key(
        self, business_id: str, idempotency_key: str
    ) -> Optional[Order]:
        """Check for existing order to ensure strict idempotency."""
        stmt = (
            select(Order)
            .where(
                Order.business_id == business_id,
                Order.idempotency_key == idempotency_key,
            )
            .options(selectinload(Order.items))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_order_by_id(self, business_id: str, order_id: str) -> Optional[Order]:
        """Fetch order by ID with line items loaded."""
        stmt = (
            select(Order)
            .where(
                Order.business_id == business_id,
                Order.id == order_id,
            )
            .options(selectinload(Order.items))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_order(
        self,
        business_id: str,
        customer_id: Optional[str],
        session_id: Optional[str],
        idempotency_key: Optional[str],
        order_type: OrderType,
        items: List[Dict[str, Any]],
        subtotal: float,
        tax: float,
        delivery_fee: float,
        total: float,
        delivery_address: Optional[str] = None,
    ) -> Order:
        """
        Create a new authoritative order within transaction.
        If idempotency_key exists, returns existing order.
        """
        if idempotency_key:
            existing = await self.get_order_by_idempotency_key(business_id, idempotency_key)
            if existing:
                return existing

        order_id = f"ord_{uuid.uuid4().hex[:8]}"

        order = Order(
            id=order_id,
            business_id=business_id,
            customer_id=customer_id,
            session_id=session_id,
            idempotency_key=idempotency_key,
            order_type=order_type,
            status=OrderStatus.CONFIRMED,
            subtotal=subtotal,
            tax=tax,
            delivery_fee=delivery_fee,
            total=total,
            delivery_address=delivery_address,
        )
        self.session.add(order)

        for item_data in items:
            order_item = OrderItem(
                order_id=order_id,
                product_id=item_data["product_id"],
                name=item_data["name"],
                unit_price=item_data["price"],
                quantity=item_data["quantity"],
                customizations=item_data.get("customizations", []),
                item_total=item_data["price"] * item_data["quantity"],
            )
            self.session.add(order_item)

        await self.session.commit()
        return await self.get_order_by_id(business_id, order_id)

    async def update_status(
        self, business_id: str, order_id: str, status: OrderStatus, reason: Optional[str] = None
    ) -> Optional[Order]:
        """Update order status (e.g. cancelled)."""
        order = await self.get_order_by_id(business_id, order_id)
        if not order:
            return None

        order.status = status
        if reason:
            order.cancellation_reason = reason

        await self.session.commit()
        return order
