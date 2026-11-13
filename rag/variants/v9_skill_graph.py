"""
RAG Variant V9: Skill Graph / GraphRAG (Agentic Group)
Traverses knowledge graph edges between Skills, Projects, Clients, Industries, and Outcomes.
Answers associative queries like 'Have I delivered X in industry Y?' with multi-hop grounding.
"""

from typing import List, Dict, Any
from rag.index.graph_index import SkillGraphIndex

class V9SkillGraphRetriever:
    def __init__(self, graph_index: SkillGraphIndex):
        self.graph_index = graph_index

    def retrieve(self, skills: List[str], industry: str = "", k: int = 5) -> List[Dict[str, Any]]:
        hits = self.graph_index.query_graph(skills, industry=industry, k=k)
        results = []
        for h in hits:
            results.append({
                "chunk_id": f"graph_{h['doc_id']}",
                "doc_id": h["doc_id"],
                "text": h["text"],
                "score": h["graph_score"],
                "variant": "V9_skill_graph",
                "metadata": {
                    "project": h.get("project"),
                    "skills": h.get("skills"),
                    "client_industry": h.get("client_industry"),
                    "outcome": h.get("outcome"),
                    "source": h.get("source")
                }
            })
        return results
