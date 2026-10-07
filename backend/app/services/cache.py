"""
Redis client and caching service per VoiceOS BRAIN §26 & §56.

Used for:
  - Short-lived session metadata
  - Caching frequently requested static business details
  - Distributed lock primitives
Authoritative transactions remain in PostgreSQL.
"""

import json
from typing import Any, Optional
import redis.asyncio as aioredis
from app.config.settings import settings


class CacheService:
    """Async Redis caching client with fallback to in-memory dictionary if Redis is offline."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._memory_cache: dict[str, str] = {}
        self._use_memory_fallback = False

    async def _get_client(self) -> Optional[aioredis.Redis]:
        if self._use_memory_fallback:
            return None

        if self._redis is None:
            try:
                self._redis = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=1.0,
                )
                await self._redis.ping()
            except Exception:
                # Fall back gracefully to memory cache if Redis not running locally
                self._use_memory_fallback = True
                self._redis = None
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        """Fetch and deserialize JSON value by key."""
        client = await self._get_client()
        if client:
            try:
                val = await client.get(key)
                return json.loads(val) if val else None
            except Exception:
                pass

        val = self._memory_cache.get(key)
        return json.loads(val) if val else None

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = 300) -> bool:
        """Serialize and store JSON value with TTL expiration."""
        payload = json.dumps(value)
        client = await self._get_client()
        if client:
            try:
                if ttl_seconds:
                    await client.setex(key, ttl_seconds, payload)
                else:
                    await client.set(key, payload)
                return True
            except Exception:
                pass

        self._memory_cache[key] = payload
        return True

    async def delete(self, key: str) -> bool:
        """Remove key from cache."""
        client = await self._get_client()
        if client:
            try:
                await client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)
        return True

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.aclose()
            self._redis = None


cache_service = CacheService()
