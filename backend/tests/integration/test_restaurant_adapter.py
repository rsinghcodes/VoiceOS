"""Integration tests for RestaurantAdapter and Database repositories."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database.models.base import Base
from app.database.models.models import (
    Business,
    Category,
    Product,
    OrderType,
    OrderStatus,
)
from app.database.repositories.repositories import CatalogRepository, OrderRepository
from app.businesses.restaurant.adapter import RestaurantAdapter
from app.agent.tools.registry import execute_tool_call


@pytest_asyncio.fixture
async def db_session():
    """Create an in-memory SQLite async database for isolated integration testing."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        # Seed test business, category, and products
        business = Business(
            id="restaurant_001",
            name="Spice Symphony Restaurant",
            business_type="restaurant",
        )
        cat = Category(id="cat_1", business_id="restaurant_001", name="Main Course")
        p1 = Product(
            id="p_1",
            business_id="restaurant_001",
            category_id="cat_1",
            name="Butter Chicken",
            price=320.0,
            is_available=True,
            inventory_count=10,
        )
        p2 = Product(
            id="p_2",
            business_id="restaurant_001",
            category_id="cat_1",
            name="Garlic Naan",
            price=60.0,
            is_available=True,
            inventory_count=20,
        )
        p3 = Product(
            id="p_3",
            business_id="restaurant_001",
            category_id="cat_1",
            name="Tandoori Fish",
            price=400.0,
            is_available=False,
            inventory_count=0,
        )

        session.add_all([business, cat, p1, p2, p3])
        await session.commit()

        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_restaurant_adapter_catalog_and_availability(db_session: AsyncSession):
    catalog_repo = CatalogRepository(db_session)
    order_repo = OrderRepository(db_session)
    adapter = RestaurantAdapter(catalog_repo=catalog_repo, order_repo=order_repo)

    # 1. Search products
    results = await adapter.search_catalog("Butter")
    assert len(results) == 1
    assert results[0]["name"] == "Butter Chicken"

    # 2. Availability
    assert await adapter.check_availability("p_1", quantity=2) is True
    assert await adapter.check_availability("p_3", quantity=1) is False  # Sold out


@pytest.mark.asyncio
async def test_restaurant_adapter_cart_and_total(db_session: AsyncSession):
    catalog_repo = CatalogRepository(db_session)
    order_repo = OrderRepository(db_session)
    adapter = RestaurantAdapter(catalog_repo=catalog_repo, order_repo=order_repo)

    cart_id = await adapter.create_cart("sess_123")
    await adapter.add_to_cart(cart_id, "p_1", quantity=1)
    await adapter.add_to_cart(cart_id, "p_2", quantity=2)

    cart = await adapter.get_cart(cart_id)
    assert len(cart["items"]) == 2
    # Subtotal: 320 + (60 * 2) = 440
    assert cart["subtotal"] == 440.0

    totals = await adapter.calculate_total(cart_id)
    assert totals["subtotal"] == 440.0
    assert totals["delivery_fee"] == 40.0
    # Tax: 440 * 0.05 = 22.0
    assert totals["tax"] == 22.0
    assert totals["total"] == 502.0


@pytest.mark.asyncio
async def test_restaurant_adapter_order_creation_and_idempotency(db_session: AsyncSession):
    catalog_repo = CatalogRepository(db_session)
    order_repo = OrderRepository(db_session)
    adapter = RestaurantAdapter(catalog_repo=catalog_repo, order_repo=order_repo)

    cart_id = await adapter.create_cart("sess_456")
    await adapter.add_to_cart(cart_id, "p_1", quantity=1)

    customer_data = {
        "customer_name": "Rohan Gupta",
        "phone": "+919876543210",
        "delivery_address": "Flat 402, Green Avenue, Delhi",
        "order_type": "delivery",
        "idempotency_key": "idem_unique_key_001",
    }

    # First transaction
    order1 = await adapter.create_transaction(cart_id, customer_data)
    assert order1["status"] == "CONFIRMED"
    order_id = order1["order_id"]

    # Re-order with same idempotency key should return original order without duplicate
    order2 = await order_repo.create_order(
        business_id="restaurant_001",
        customer_id=None,
        session_id=None,
        idempotency_key="idem_unique_key_001",
        order_type=OrderType.DELIVERY,
        items=[],
        subtotal=320.0,
        tax=16.0,
        delivery_fee=40.0,
        total=376.0,
    )
    assert order2.id == order_id


@pytest.mark.asyncio
async def test_tool_execution_with_real_restaurant_adapter(db_session: AsyncSession):
    catalog_repo = CatalogRepository(db_session)
    order_repo = OrderRepository(db_session)
    adapter = RestaurantAdapter(catalog_repo=catalog_repo, order_repo=order_repo)

    # 1. Search tool
    search_res = await execute_tool_call(
        tool_name="search_catalog",
        args={"query": "chicken"},
        adapter=adapter,
    )
    assert search_res["success"] is True
    assert len(search_res["data"]) >= 1

    # 2. Add to cart tool
    cart_id = await adapter.create_cart("session_tool_test")
    add_res = await execute_tool_call(
        tool_name="add_to_cart",
        args={
            "cart_id": cart_id,
            "product_id": "p_1",
            "quantity": 1,
            "customizations": ["Extra spicy"],
        },
        adapter=adapter,
    )
    assert add_res["success"] is True
    assert add_res["data"]["subtotal"] == 320.0
