"""
RAG Variant V4: Outcome-Aware Ranking (Ranking Group)
Applies dynamic outcome multipliers to retrieved evidence chunks.
Evidence and past proposals that historically WON contracts receive a +25% score boost,
while REPLIED items receive a +10% boost, biasing retrieval toward empirically successful proof points.
"""

from typing import List, Dict, Any
from rag.variants.v2_hybrid import V2HybridRetriever

class V4OutcomeAwareRetriever:
    def __init__(self, base_retriever: V2HybridRetriever, win_boost: float = 1.25, reply_boost: float = 1.10):
        self.base_retriever = base_retriever
        self.win_boost = win_boost
        self.reply_boost = reply_boost

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        candidates = self.base_retriever.retrieve(query, k=k*3)
        
        for c in candidates:
            outcome = str(c.get("metadata", {}).get("outcome", "")).lower()
            base_score = c.get("score", 0.0)
            
            if "won" in outcome or "5/5" in outcome or "verified" in outcome:
                c["score"] = round(base_score * self.win_boost, 5)
                c["outcome_multiplier"] = self.win_boost
            elif "replied" in outcome or "interview" in outcome:
                c["score"] = round(base_score * self.reply_boost, 5)
                c["outcome_multiplier"] = self.reply_boost
            else:
                c["outcome_multiplier"] = 1.0

        candidates.sort(key=lambda x: x["score"], reverse=True)
        top_k = candidates[:k]
        for c in top_k:
            c["variant"] = "V4_outcome_aware"
        return top_k
