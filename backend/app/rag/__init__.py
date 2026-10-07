"""RAG module public exports."""

from app.rag.chunking.chunker import recursive_chunk_text, DocumentChunk
from app.rag.embeddings.provider import EmbeddingProvider, FastEmbeddingProvider
from app.rag.ingestion.store import QdrantKnowledgeStore
from app.rag.retrieval.retriever import KnowledgeRetriever
from app.rag.reranking.reranker import CrossEncoderReranker
from app.rag.evaluation import RAGEvaluator

__all__ = [
    "recursive_chunk_text",
    "DocumentChunk",
    "EmbeddingProvider",
    "FastEmbeddingProvider",
    "QdrantKnowledgeStore",
    "KnowledgeRetriever",
    "CrossEncoderReranker",
    "RAGEvaluator",
]
