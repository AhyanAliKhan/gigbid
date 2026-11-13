"""
RAG BM25 Index
Lexical keyword search using BM25Okapi for exact tool, acronym, and library matching.
"""

from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi

class BM25Index:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.bm25: BM25Okapi = None

    def _tokenize(self, text: str) -> List[str]:
        return [t.lower() for t in text.replace(",", " ").replace(".", " ").replace("-", " ").split() if len(t) > 1]

    def fit_and_index(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        if not chunks:
            return
        corpus = [self._tokenize(f"{c['text']} {' '.join(c.get('skills', []))}") for c in chunks]
        self.bm25 = BM25Okapi(corpus)

    def query(self, query_text: str, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if not self.chunks or self.bm25 is None:
            return []
        tokenized_q = self._tokenize(query_text)
        if not tokenized_q:
            return []
        scores = self.bm25.get_scores(tokenized_q)
        import numpy as np
        top_indices = np.argsort(scores)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append((self.chunks[idx], float(scores[idx])))
        return results
