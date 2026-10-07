"""
RAG evaluation metrics calculator per VoiceOS BRAIN §48.
Measures Recall@K, Precision@K, and Groundedness for knowledge retrieval.
"""

from typing import List, Set, Dict, Any


class RAGEvaluator:
    """Computes deterministic retrieval evaluation metrics."""

    @staticmethod
    def calculate_metrics(
        expected_chunk_ids: Set[str],
        retrieved_chunk_ids: List[str],
    ) -> Dict[str, float]:
        """
        Calculate Recall@K, Precision@K, and MRR.
        """
        if not expected_chunk_ids:
            return {"recall": 1.0, "precision": 1.0, "mrr": 1.0}

        retrieved_set = set(retrieved_chunk_ids)
        hits = expected_chunk_ids.intersection(retrieved_set)

        recall = len(hits) / len(expected_chunk_ids)
        precision = len(hits) / max(1, len(retrieved_chunk_ids))

        # Mean Reciprocal Rank (MRR)
        mrr = 0.0
        for rank, cid in enumerate(retrieved_chunk_ids, start=1):
            if cid in expected_chunk_ids:
                mrr = 1.0 / rank
                break

        return {
            "recall": round(recall, 4),
            "precision": round(precision, 4),
            "mrr": round(mrr, 4),
        }
