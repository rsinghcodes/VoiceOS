"""
RAG multi-tenant retrieval with strict business_id metadata filtering.
"""

from typing import List, Dict, Any, Optional
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.rag.ingestion.store import QdrantKnowledgeStore


class KnowledgeRetriever:
    """
    Retrieves semantic context for agent conversations, enforcing
    tenant isolation (business_id) and optional category/document filtering.
    """

    def __init__(self, store: QdrantKnowledgeStore):
        self.store = store

    async def retrieve(
        self,
        business_id: str,
        query: str,
        top_k: int = 3,
        document_type: Optional[str] = None,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Embeds the query and retrieves the Top-K matching points with metadata filtering.
        """
        query_vector = await self.store.embedder.embed_query(query)

        # Multi-tenant isolation filter: MUST match business_id
        must_conditions = [
            FieldCondition(
                key="business_id",
                match=MatchValue(value=business_id),
            )
        ]

        if document_type:
            must_conditions.append(
                FieldCondition(
                    key="document_type",
                    match=MatchValue(value=document_type),
                )
            )

        query_filter = Filter(must=must_conditions)

        search_result = self.store.client.query_points(
            collection_name=self.store.COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=score_threshold,
            with_payload=True,
        )

        results = []
        for point in search_result.points:
            payload = point.payload or {}
            results.append({
                "chunk_id": str(point.id),
                "score": round(float(point.score), 4),
                "text": payload.get("text", ""),
                "document_type": payload.get("document_type"),
                "business_id": payload.get("business_id"),
                "metadata": payload,
            })

        return results
