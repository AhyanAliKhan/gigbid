"""
RAG Variant V1: Requirement Decomposition (Query Group)
Extracts discrete technical and domain requirements from the job post,
executes focused retrieval per requirement, and merges candidate lists via reciprocal rank aggregation.
"""

from typing import List, Dict, Any
from rag.index.vector_index import DenseVectorIndex

class V1RequirementDecompRetriever:
    def __init__(self, vector_index: DenseVectorIndex):
        self.vector_index = vector_index

    def _extract_requirements(self, job_title: str, job_description: str, skills: List[str]) -> List[str]:
        reqs = list(skills)
        if job_title and job_title not in reqs:
            reqs.append(job_title)
        
        # Extract sentence-level deliverable requirements
        sentences = [s.strip() for s in job_description.replace("\n", ". ").split(".") if len(s.strip()) > 15]
        for s in sentences[:3]:
            reqs.append(s)
        return reqs

    def retrieve(self, job_title: str, job_description: str, skills: List[str], k: int = 5) -> List[Dict[str, Any]]:
        reqs = self._extract_requirements(job_title, job_description, skills)
        if not reqs:
            reqs = [f"{job_title} {job_description}"]

        merged_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        for req in reqs:
            hits = self.vector_index.query(req, k=k*2)
            for rank, (chunk, score) in enumerate(hits, start=1):
                cid = chunk["chunk_id"]
                chunk_map[cid] = chunk
                # Reciprocal rank contribution
                merged_scores[cid] = merged_scores.get(cid, 0.0) + (1.0 / (20.0 + rank))

        sorted_cids = sorted(merged_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        results = []
        for cid, score in sorted_cids:
            chunk = chunk_map[cid]
            results.append({
                "chunk_id": cid,
                "doc_id": chunk["doc_id"],
                "text": chunk["text"],
                "score": round(score, 4),
                "variant": "V1_requirement_decomp",
                "metadata": {
                    "project": chunk.get("project"),
                    "skills": chunk.get("skills"),
                    "outcome": chunk.get("outcome"),
                    "source": chunk.get("source")
                }
            })
        return results
