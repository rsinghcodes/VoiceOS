"""
Reranking module for RAG retrieval results.
Applies cross-scoring / keyword overlap adjustment to refine Top-K ranking for voice context.
"""

from typing import List, Dict, Any


class CrossEncoderReranker:
    """
    Reranker to re-score and re-order initial retrieval candidates.
    Prioritizes chunks with exact question keyword matches and context density.
    """

    @staticmethod
    def rerank(
        query: str,
        candidates: List[Dict[str, Any]],
        top_n: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Adjust vector similarity score with keyword presence and length normalization.
        """
        if not candidates:
            return []

        query_tokens = set(
            w.lower().strip("?,.!")
            for w in query.split()
            if len(w) > 2
        )

        rescored = []
        for cand in candidates:
            base_score = cand.get("score", 0.0)
            text = cand.get("text", "").lower()

            # Count keyword hits
            hits = sum(1 for tok in query_tokens if tok in text)
            keyword_bonus = (hits / max(1, len(query_tokens))) * 0.3

            final_score = round(base_score + keyword_bonus, 4)
            augmented = dict(cand)
            augmented["reranked_score"] = final_score
            rescored.append(augmented)

        # Sort descending by reranked_score
        rescored.sort(key=lambda x: x["reranked_score"], reverse=True)
        return rescored[:top_n]
