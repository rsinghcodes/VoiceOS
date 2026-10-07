"""
RAG document ingestion into Qdrant vector database with multi-tenant metadata isolation.
"""

import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.rag.chunking.chunker import recursive_chunk_text, DocumentChunk
from app.rag.embeddings.provider import EmbeddingProvider, FastEmbeddingProvider


class QdrantKnowledgeStore:
    """
    Multi-tenant vector store backed by Qdrant.
    Enforces strict business_id scoping on all upserts and queries.
    """

    COLLECTION_NAME = "voiceos_knowledge"

    def __init__(
        self,
        client: Optional[QdrantClient] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        location: Optional[str] = None,
    ):
        from app.config.settings import settings

        if client is not None:
            self.client = client
        elif location:
            self.client = QdrantClient(location=location)
        else:
            q_url = url or settings.qdrant_url
            q_key = api_key or settings.qdrant_api_key
            if q_url:
                self.client = QdrantClient(url=q_url, api_key=q_key)
            else:
                self.client = QdrantClient(location=":memory:")

        self.embedder = embedding_provider or FastEmbeddingProvider()
        self._ensure_collection()

    def _ensure_collection(self):
        """Create Qdrant collection if not already existing."""
        collections = [c.name for c in self.client.get_collections().collections]
        if self.COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.embedder.dimension,
                    distance=Distance.COSINE,
                ),
            )

    async def ingest_document(
        self,
        business_id: str,
        document_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
    ) -> List[str]:
        """
        Chunk and ingest a document tagged with business_id into Qdrant.
        """
        metadata = metadata or {}
        raw_chunks = recursive_chunk_text(content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if not raw_chunks:
            return []

        embeddings = await self.embedder.embed_texts(raw_chunks)
        points = []
        chunk_ids = []

        for idx, (chunk_text, vector) in enumerate(zip(raw_chunks, embeddings)):
            point_id = str(uuid.uuid4())
            chunk_ids.append(point_id)

            payload = {
                "business_id": business_id,
                "document_type": document_type,
                "text": chunk_text,
                "chunk_index": idx,
                **metadata,
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
        )

        return chunk_ids
