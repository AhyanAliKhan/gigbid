"""
RAG Skill Graph Index (GraphRAG)
Constructs an entity-relationship knowledge graph linking Skills, Projects, Clients, Industries, and Outcomes.
Enables multi-hop associative queries (e.g., 'Have I done X in industry Y for client Z?').
"""

from typing import List, Dict, Any, Set, Tuple

class SkillGraphIndex:
    def __init__(self):
        # Graph structure: adjacency maps
        # skill -> set(project_ids)
        # industry -> set(project_ids)
        # project_id -> {details, skills, industry, outcome}
        self.skill_to_projects: Dict[str, Set[str]] = {}
        self.industry_to_projects: Dict[str, Set[str]] = {}
        self.projects: Dict[str, Dict[str, Any]] = {}

    def fit_and_index(self, chunks: List[Dict[str, Any]]):
        for c in chunks:
            pid = c.get("doc_id") or c.get("chunk_id")
            if pid not in self.projects:
                self.projects[pid] = {
                    "id": pid,
                    "title": c.get("project", ""),
                    "summary": c.get("text", "")[:200],
                    "skills": set(c.get("skills", [])),
                    "industry": c.get("client_industry", "General"),
                    "outcome": c.get("outcome", "verified"),
                    "source": c.get("source", "")
                }
            else:
                self.projects[pid]["skills"].update(c.get("skills", []))

            # Populate edges
            ind = c.get("client_industry", "General").lower()
            self.industry_to_projects.setdefault(ind, set()).add(pid)
            
            for sk in c.get("skills", []):
                self.skill_to_projects.setdefault(sk.lower(), set()).add(pid)

    def query_graph(self, skills: List[str], industry: str = "", k: int = 5) -> List[Dict[str, Any]]:
        candidate_scores: Dict[str, float] = {}
        ind_lower = industry.lower()

        # Multi-hop intersection
        for sk in skills:
            sk_lower = sk.lower()
            matched_pids = self.skill_to_projects.get(sk_lower, set())
            for pid in matched_pids:
                candidate_scores[pid] = candidate_scores.get(pid, 0.0) + 1.0

        # Industry affinity boost
        if ind_lower and ind_lower in self.industry_to_projects:
            for pid in self.industry_to_projects[ind_lower]:
                candidate_scores[pid] = candidate_scores.get(pid, 0.0) + 1.5

        sorted_pids = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        results = []
        for pid, score in sorted_pids:
            p_data = self.projects[pid]
            results.append({
                "doc_id": pid,
                "project": p_data["title"],
                "text": p_data["summary"],
                "skills": list(p_data["skills"]),
                "client_industry": p_data["industry"],
                "outcome": p_data["outcome"],
                "source": p_data["source"],
                "graph_score": round(score, 2)
            })
        return results
