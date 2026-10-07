"""
Unit and integration tests for Phase 5 — RAG Pipeline:
  - Chunking
  - Embeddings
  - Qdrant Multi-tenant Ingestion
  - Knowledge Retrieval with tenant isolation
  - Reranking
  - RAG Evaluation (Recall@K, Precision@K, MRR)
"""

import pytest
from app.rag.chunking.chunker import recursive_chunk_text
from app.rag.embeddings.provider import FastEmbeddingProvider
from app.rag.ingestion.store import QdrantKnowledgeStore
from app.rag.retrieval.retriever import KnowledgeRetriever
from app.rag.reranking.reranker import CrossEncoderReranker
from app.rag.evaluation import RAGEvaluator
from app.businesses.restaurant.adapter import RestaurantAdapter


def test_recursive_chunk_text():
    sample_text = (
        "Spice Symphony is open Monday through Sunday from 11:00 AM to 11:00 PM.\n\n"
        "We offer home delivery within a 7 kilometer radius. Minimum delivery order is ₹150.\n\n"
        "All our poultry and meat dishes are 100% Halal certified and prepared fresh daily."
    )
    chunks = recursive_chunk_text(sample_text, chunk_size=120, chunk_overlap=20)
    assert len(chunks) >= 2
    assert all(len(c) > 0 for c in chunks)


@pytest.mark.asyncio
async def test_fast_embedding_provider():
    embedder = FastEmbeddingProvider(dimension=64)
    assert embedder.dimension == 64

    vector = await embedder.embed_query("butter chicken delivery")
    assert len(vector) == 64
    assert any(v != 0.0 for v in vector)

    batch_vectors = await embedder.embed_texts(["hello", "world"])
    assert len(batch_vectors) == 2
    assert len(batch_vectors[0]) == 64


@pytest.mark.asyncio
async def test_qdrant_ingestion_and_multi_tenant_isolation():
    store = QdrantKnowledgeStore(location=":memory:")
    retriever = KnowledgeRetriever(store)

    # 1. Ingest document for restaurant_001
    await store.ingest_document(
        business_id="restaurant_001",
        document_type="policy",
        content="Spice Symphony Restaurant provides free delivery for orders above 500 rupees.",
        metadata={"category": "delivery"},
    )

    # 2. Ingest document for another tenant (salon_001)
    await store.ingest_document(
        business_id="salon_001",
        document_type="policy",
        content="ABC Salon offers 20% discount on first haircut booking.",
        metadata={"category": "discounts"},
    )

    # 3. Query for restaurant_001: must ONLY retrieve restaurant_001 documents
    res_restaurant = await retriever.retrieve(
        business_id="restaurant_001",
        query="delivery order fee",
        top_k=5,
    )
    assert len(res_restaurant) >= 1
    assert all(doc["business_id"] == "restaurant_001" for doc in res_restaurant)
    assert "Spice Symphony" in res_restaurant[0]["text"]

    # 4. Tenant isolation check: salon_001 cannot see restaurant_001 documents
    res_salon = await retriever.retrieve(
        business_id="salon_001",
        query="haircut booking discount",
        top_k=5,
    )
    assert len(res_salon) >= 1
    assert all(doc["business_id"] == "salon_001" for doc in res_salon)
    assert "ABC Salon" in res_salon[0]["text"]


@pytest.mark.asyncio
async def test_cross_encoder_reranker():
    candidates = [
        {"score": 0.70, "text": "We deliver food around the clock."},
        {"score": 0.65, "text": "Minimum delivery order amount is 150 rupees."},
    ]
    query = "What is the minimum delivery order amount?"
    reranked = CrossEncoderReranker.rerank(query=query, candidates=candidates, top_n=2)

    assert len(reranked) == 2
    # The candidate containing 'minimum delivery order amount' should be ranked #1
    assert "150 rupees" in reranked[0]["text"]
    assert reranked[0]["reranked_score"] > reranked[1]["reranked_score"]


def test_rag_evaluator_metrics():
    expected = {"chunk_1", "chunk_2"}
    retrieved = ["chunk_2", "chunk_3", "chunk_4"]

    metrics = RAGEvaluator.calculate_metrics(
        expected_chunk_ids=expected,
        retrieved_chunk_ids=retrieved,
    )

    assert metrics["recall"] == 0.5  # 1 out of 2 expected
    assert metrics["precision"] == round(1 / 3, 4)
    assert metrics["mrr"] == 1.0  # Hit at position 1


@pytest.mark.asyncio
async def test_restaurant_adapter_with_qdrant_retriever():
    store = QdrantKnowledgeStore(location=":memory:")
    retriever = KnowledgeRetriever(store)

    # Ingest allergen & hygiene guidelines
    await store.ingest_document(
        business_id="restaurant_001",
        document_type="faq",
        content="All our meals are cooked in peanut-free oils and prepared in an FSSAI certified kitchen.",
    )

    adapter = RestaurantAdapter(knowledge_retriever=retriever)
    results = await adapter.search_knowledge("peanut allergen and oil")

    assert len(results) >= 1
    assert "peanut-free" in results[0]["answer"].lower()
