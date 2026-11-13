"""
RAG Variant V2: Hybrid BM25 + Dense with Reciprocal Rank Fusion (Retrieval Group)
Combines dense semantic vector retrieval with BM25 lexical keyword matching using RRF (k=60).
Captures both semantic meaning and exact technical libraries / toolnames ('Celery', 'dbt', 'Pinecone').
"""

from typing import List, Dict, Any
from rag.index.vector_index import DenseVectorIndex
from rag.index.bm25_index import BM25Index

class V2HybridRetriever:
    def __init__(self, vector_index: DenseVectorIndex, bm25_index: BM25Index, rrf_k: int = 60):
        self.vector_index = vector_index
        self.bm25_index = bm25_index
        self.rrf_k = rrf_k

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        # 1. Retrieve top-20 from Dense
        dense_hits = self.vector_index.query(query, k=20)
        
        # 2. Retrieve top-20 from BM25
        bm25_hits = self.bm25_index.query(query, k=20)

        # 3. Reciprocal Rank Fusion
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        for rank, (chunk, score) in enumerate(dense_hits, start=1):
            cid = chunk["chunk_id"]
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        for rank, (chunk, score) in enumerate(bm25_hits, start=1):
            cid = chunk["chunk_id"]
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        sorted_cids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:k]

        results = []
        for cid, rrf_score in sorted_cids:
            chunk = chunk_map[cid]
            results.append({
                "chunk_id": cid,
                "doc_id": chunk["doc_id"],
                "text": chunk["text"],
                "score": round(rrf_score, 5),
                "variant": "V2_hybrid_rrf",
                "metadata": {
                    "project": chunk.get("project"),
                    "skills": chunk.get("skills"),
                    "outcome": chunk.get("outcome"),
                    "source": chunk.get("source")
                }
            })
        return results
