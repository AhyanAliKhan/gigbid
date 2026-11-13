"""
RAG Ingestion: Multi-Format Document Loaders
Loads CVs, Case Studies, Repository READMEs & Code, Client Reviews, and Past Proposals.
"""

import os
import json
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSONAS_DIR = os.path.join(BASE_DIR, "data", "personas")

class DocumentLoader:
    def __init__(self, personas_dir: Optional[str] = None):
        self.personas_dir = personas_dir or PERSONAS_DIR

    def load_all_documents_for_persona(self, persona_id: str) -> List[Dict[str, Any]]:
        p_dir = os.path.join(self.personas_dir, persona_id)
        if not os.path.exists(p_dir):
            raise FileNotFoundError(f"Persona directory '{p_dir}' not found.")

        documents = []

        # 1. Ingest CV
        cv_path = os.path.join(p_dir, "cv.md")
        if os.path.exists(cv_path):
            with open(cv_path, "r", encoding="utf-8") as f:
                documents.append({
                    "id": f"CV-{persona_id}",
                    "persona": persona_id,
                    "type": "cv",
                    "project": "Curriculum Vitae",
                    "skills": [],
                    "date": "2026-01-01",
                    "client_industry": "General",
                    "outcome": "verified",
                    "source": cv_path,
                    "text": f.read()
                })

        # 2. Ingest Case Studies
        cs_dir = os.path.join(p_dir, "case_studies")
        cs_meta_file = os.path.join(p_dir, "case_studies.json")
        cs_meta_map = {}
        if os.path.exists(cs_meta_file):
            with open(cs_meta_file, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    cs_meta_map[item["id"]] = item

        if os.path.exists(cs_dir):
            for fname in os.listdir(cs_dir):
                if fname.endswith(".md"):
                    cs_id = fname.replace(".md", "")
                    meta = cs_meta_map.get(cs_id, {})
                    fpath = os.path.join(cs_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        text = f.read()
                    documents.append({
                        "id": cs_id,
                        "persona": persona_id,
                        "type": "case_study",
                        "project": meta.get("title", cs_id),
                        "skills": meta.get("skills", []),
                        "date": meta.get("date", "2025-06-01"),
                        "client_industry": meta.get("client_industry", "Technology"),
                        "outcome": meta.get("verified_outcome", "Delivered successfully"),
                        "source": fpath,
                        "text": text
                    })

        # 3. Ingest Repositories & Code
        repos_file = os.path.join(p_dir, "repos.json")
        if os.path.exists(repos_file):
            with open(repos_file, "r", encoding="utf-8") as f:
                repos = json.load(f)
            for r in repos:
                repo_dir = os.path.join(p_dir, "repos", r["repo_name"])
                readme_path = os.path.join(repo_dir, "README.md")
                readme_text = ""
                if os.path.exists(readme_path):
                    with open(readme_path, "r", encoding="utf-8") as f:
                        readme_text = f.read()
                
                documents.append({
                    "id": f"REPO-{r['repo_name']}",
                    "persona": persona_id,
                    "type": "repository",
                    "project": r["repo_name"],
                    "skills": [r["primary_language"]],
                    "date": "2025-01-01",
                    "client_industry": "Open Source",
                    "outcome": f"Stars: {r.get('stars', 0)}",
                    "source": r.get("url", f"https://github.com/freelancer/{r['repo_name']}"),
                    "text": f"{r['description']}\n\n{readme_text}"
                })

        # 4. Ingest Client Reviews
        reviews_file = os.path.join(p_dir, "reviews.json")
        if os.path.exists(reviews_file):
            with open(reviews_file, "r", encoding="utf-8") as f:
                reviews = json.load(f)
            for rev in reviews:
                documents.append({
                    "id": rev["review_id"],
                    "persona": persona_id,
                    "type": "review",
                    "project": rev.get("project_name", "Client Engagement"),
                    "skills": [],
                    "date": rev.get("date", "2025-04-01"),
                    "client_industry": "Client Feedback",
                    "outcome": f"Rating: {rev.get('rating', 5.0)}/5.0",
                    "source": f"reviews/{rev['review_id']}.json",
                    "text": f"Review by {rev.get('client_name')}: {rev.get('feedback')}"
                })

        # 5. Ingest Past Proposals with Outcomes (won / replied / ignored)
        proposals_file = os.path.join(p_dir, "past_proposals.json")
        if os.path.exists(proposals_file):
            with open(proposals_file, "r", encoding="utf-8") as f:
                proposals = json.load(f)
            for prop in proposals:
                documents.append({
                    "id": prop["proposal_id"],
                    "persona": persona_id,
                    "type": "past_proposal",
                    "project": prop.get("job_title", "Past Bid"),
                    "skills": prop.get("skills", []),
                    "date": prop.get("submitted_at", "2024-09-01"),
                    "client_industry": "Marketplace Bid",
                    "outcome": prop.get("outcome", "ignored"), # won, replied, ignored
                    "source": f"past_proposals/{prop['proposal_id']}.json",
                    "text": prop.get("cover_letter", "")
                })

        return documents
