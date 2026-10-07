"""Unit tests for Phase 6 — Production Engineering: CacheService & TelemetryTracker."""

import pytest
from app.services.cache import CacheService
from app.observability.telemetry import TelemetryTracker


@pytest.mark.asyncio
async def test_cache_service_set_get_delete():
    cache = CacheService()

    # 1. Set cache item
    test_key = "session_meta_123"
    test_val = {"customer_id": "cust_456", "cart_items_count": 3}
    await cache.set(test_key, test_val, ttl_seconds=60)

    # 2. Get cache item
    retrieved = await cache.get(test_key)
    assert retrieved is not None
    assert retrieved["customer_id"] == "cust_456"
    assert retrieved["cart_items_count"] == 3

    # 3. Delete cache item
    await cache.delete(test_key)
    assert await cache.get(test_key) is None


def test_telemetry_tracker_stage_measurements():
    tracker = TelemetryTracker(trace_id="test_voice_trace_01")

    # Measure synthetic stage durations
    with tracker.measure("stt_latency"):
        pass

    with tracker.measure("intent_classification"):
        pass

    with tracker.measure("tool_execution"):
        pass

    tracker.record_metric("business_id", "restaurant_001")
    payload = tracker.to_dict()

    assert payload["trace_id"] == "test_voice_trace_01"
    assert "stt_latency" in payload["stages"]
    assert "intent_classification" in payload["stages"]
    assert "tool_execution" in payload["stages"]
    assert payload["metadata"]["business_id"] == "restaurant_001"
    assert payload["total_latency_ms"] >= 0.0
