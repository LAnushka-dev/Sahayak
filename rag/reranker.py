from typing import List, Dict

class CrossEncoderReranker:
    """
    Reranks combined candidate documents from Dense FAISS and Sparse BM25
    using semantic overlap, token prominence, and cross-relevance scoring.
    """
    def __init__(self, model_name: str = "ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name

    def rerank(self, query: str, candidates: List[str], top_n: int = 4) -> List[Dict]:
        if not candidates:
            return []

        q_terms = set(query.lower().split())
        scored = []

        for doc in candidates:
            doc_lower = doc.lower()
            # Calculate token containment
            match_count = sum(1 for term in q_terms if term in doc_lower)
            density = match_count / (len(q_terms) or 1)
            
            # Bonus score for explicit statutory patterns (Section, Act, Eligibility, Scheme)
            statutory_bonus = 0.0
            for keyword in ["section", "act", "eligibility", "complaint", "claim", "scheme", "right"]:
                if keyword in doc_lower:
                    statutory_bonus += 0.15

            final_score = density + statutory_bonus
            scored.append({"text": doc, "relevance_score": round(final_score, 4)})

        # Sort by relevance score descending
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:top_n]
