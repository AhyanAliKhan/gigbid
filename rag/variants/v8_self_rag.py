"""
RAG Variant V8: Corrective / Self-RAG Loop (Agentic Group)
Implements an active evaluation loop:
1. Retrieves initial candidate evidence.
2. Grades candidate relevance against a strict quality threshold.
3. If relevance is low, expands/rewrites query terms and performs second-chance retrieval.
4. If still insufficient, explicitly returns empty/fallback flag preventing the writer from hallucinating claims.
"""

from typing import List, Dict, Any, Tuple
from rag.variants.v2_hybrid import V2HybridRetriever

class V8SelfRAGRetriever:
    def __init__(self, base_retriever: V2HybridRetriever, relevance_threshold: float = 0.015):
        self.base_retriever = base_retriever
        self.threshold = relevance_threshold

    def _grade_evidence(self, candidates: List[Dict[str, Any]], query: str) -> Tuple[bool, float]:
        if not candidates:
            return False, 0.0
        top_score = candidates[0].get("score", 0.0)
        # Check if top score clears threshold
        is_relevant = top_score >= self.threshold
        return is_relevant, top_score

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # Pass 1: Initial retrieval
        candidates = self.base_retriever.retrieve(query, k=k)
        is_relevant, top_score = self._grade_evidence(candidates, query)

        if is_relevant:
            for c in candidates:
                c["variant"] = "V8_self_rag_pass1"
            return candidates

        # Pass 2: Query Rewriting / Term Expansion
        terms = [t for t in query.replace(",", " ").split() if len(t) > 3]
        expanded_query = f"{' '.join(terms[:4])} production implementation architecture"
        second_pass = self.base_retriever.retrieve(expanded_query, k=k)
        is_relevant_p2, top_score_p2 = self._grade_evidence(second_pass, expanded_query)

        if is_relevant_p2:
            for c in second_pass:
                c["variant"] = "V8_self_rag_pass2_rewritten"
            return second_pass

        # If evidence is truly missing, refuse to claim
        return []
