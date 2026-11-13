"""
RAG Variant V0: Baseline Naive Dense Retrieval
Fixed chunks, top-k cosine similarity evaluated directly over the entire concatenated job post.
"""

from typing import List, Dict, Any
from rag.index.vector_index import DenseVectorIndex

class V0NaiveRetriever:
    def __init__(self, vector_index: DenseVectorIndex):
        self.vector_index = vector_index

    def retrieve(self, job_title: str, job_description: str = "", k: int = 5) -> List[Dict[str, Any]]:
        query_text = f"{job_title} {job_description}".strip()
        hits = self.vector_index.query(query_text, k=k)
        
        results = []
        for chunk, score in hits:
            results.append({
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "text": chunk["text"],
                "score": score,
                "variant": "V0_naive",
                "metadata": {
                    "project": chunk.get("project"),
                    "skills": chunk.get("skills"),
                    "outcome": chunk.get("outcome"),
                    "source": chunk.get("source")
                }
            })
        return results
