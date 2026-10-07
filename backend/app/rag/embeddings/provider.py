"""
Embedding provider interface and implementations.
Includes deterministic hash-based embedding for testing/fallback and standard API-based embedding.
"""

from abc import ABC, abstractmethod
from typing import List
import hashlib
import math


class EmbeddingProvider(ABC):
    """Abstract contract for text embeddings."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension."""
        ...

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a list of texts."""
        ...

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        """Compute embedding for a single query string."""
        ...


class FastEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic pseudo-semantic embedding generator using text feature hashing.
    Used for instant unit testing, local execution, and offline environments without external API calls.
    """

    def __init__(self, dimension: int = 128):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def _generate_vector(self, text: str) -> List[float]:
        clean = text.lower().strip()
        words = clean.split()
        vector = [0.0] * self._dim

        for idx, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            pos = h % self._dim
            weight = 1.0 / (idx + 1) ** 0.5
            vector[pos] += weight

        # Normalize to unit length
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0.0:
            vector = [round(v / norm, 5) for v in vector]
        return vector

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(t) for t in texts]

    async def embed_query(self, query: str) -> List[float]:
        return self._generate_vector(query)
