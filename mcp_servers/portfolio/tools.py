"""
Portfolio MCP Server Tools
Provides read-only access to verified freelancer portfolio evidence.
"""

import os
import json
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSONAS_DIR = os.path.join(BASE_DIR, "data", "personas")

def get_active_persona_id() -> str:
    return os.environ.get("ACTIVE_PERSONA", "alex_chen_aiml")

def load_persona_data(persona_id: Optional[str] = None) -> Dict[str, Any]:
    pid = persona_id or get_active_persona_id()
    p_dir = os.path.join(PERSONAS_DIR, pid)
    
    case_studies = []
    cs_file = os.path.join(p_dir, "case_studies.json")
    if os.path.exists(cs_file):
        with open(cs_file, "r", encoding="utf-8") as f:
            case_studies = json.load(f)

    repos = []
    r_file = os.path.join(p_dir, "repos.json")
    if os.path.exists(r_file):
        with open(r_file, "r", encoding="utf-8") as f:
            repos = json.load(f)

    reviews = []
    rev_file = os.path.join(p_dir, "reviews.json")
    if os.path.exists(rev_file):
        with open(rev_file, "r", encoding="utf-8") as f:
            reviews = json.load(f)

    past_proposals = []
    prop_file = os.path.join(p_dir, "past_proposals.json")
    if os.path.exists(prop_file):
        with open(prop_file, "r", encoding="utf-8") as f:
            past_proposals = json.load(f)

    return {
        "persona_id": pid,
        "case_studies": case_studies,
        "repos": repos,
        "reviews": reviews,
        "past_proposals": past_proposals
    }

def search_evidence(
    requirement: str,
    k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    persona_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search verified portfolio evidence matching a client requirement.
    
    Args:
        requirement: The skill, deliverable, or domain requirement to match.
        k: Maximum number of evidence items to return (default: 5).
        filters: Optional filters (e.g. {'type': 'case_study', 'client_industry': 'Fintech'}).
        persona_id: Optional persona identifier. Defaults to active persona.
        
    Returns:
        List of structured evidence records with source, date, skills, and verified outcome.
    """
    data = load_persona_data(persona_id)
    req_terms = [t.lower().strip() for t in requirement.replace(",", " ").split() if len(t.strip()) > 2]
    candidates = []

    # 1. Search Case Studies
    for cs in data["case_studies"]:
        if filters and filters.get("type") and filters["type"] != "case_study":
            continue
        if filters and filters.get("client_industry") and filters["client_industry"].lower() != cs.get("client_industry", "").lower():
            continue

        match_count = 0
        cs_text = f"{cs['title']} {cs['summary']} {' '.join(cs.get('skills', []))} {cs.get('client_industry', '')}".lower()
        for term in req_terms:
            if term in cs_text:
                match_count += 1
        
        # Skill exact matches get extra weight
        for skill in cs.get("skills", []):
            if skill.lower() in [t.lower() for t in req_terms]:
                match_count += 2

        score = match_count / max(1, len(req_terms))
        candidates.append({
            "evidence_id": cs["id"],
            "type": "case_study",
            "title": cs["title"],
            "summary": cs["summary"],
            "skills": cs.get("skills", []),
            "client_industry": cs.get("client_industry"),
            "outcome": cs.get("verified_outcome", "Delivered successfully"),
            "date": cs.get("date"),
            "source": f"data/personas/{data['persona_id']}/case_studies/{cs['id']}.md",
            "relevance_score": round(score, 3)
        })

    # 2. Search Repositories
    for r in data["repos"]:
        if filters and filters.get("type") and filters["type"] != "repo":
            continue
        r_text = f"{r['repo_name']} {r['description']} {r['primary_language']}".lower()
        match_count = sum(1 for t in req_terms if t in r_text)
        score = match_count / max(1, len(req_terms))
        candidates.append({
            "evidence_id": f"REPO-{r['repo_name']}",
            "type": "repository",
            "title": r["repo_name"],
            "summary": r["description"],
            "skills": [r["primary_language"]],
            "client_industry": "Open Source",
            "outcome": f"Public repository ({r['stars']} stars)",
            "date": "2025-06-01",
            "source": r["url"],
            "relevance_score": round(score, 3)
        })

    # Sort descending by relevance score
    candidates.sort(key=lambda x: x["relevance_score"], reverse=True)
    return candidates[:k]

def get_case_study(id: str, persona_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve full details for a specific case study by ID."""
    data = load_persona_data(persona_id)
    for cs in data["case_studies"]:
        if cs["id"].lower() == id.lower():
            md_path = os.path.join(PERSONAS_DIR, data["persona_id"], "case_studies", f"{cs['id']}.md")
            full_text = cs["summary"]
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    full_text = f.read()
            return {**cs, "full_text": full_text}
    return {"error": f"Case study '{id}' not found."}

def list_skills(persona_id: Optional[str] = None) -> List[str]:
    """List all verified technical skills claimed by the active persona."""
    data = load_persona_data(persona_id)
    all_skills = set()
    for cs in data["case_studies"]:
        all_skills.update(cs.get("skills", []))
    for r in data["repos"]:
        all_skills.add(r.get("primary_language", "Python"))
    return sorted(list(all_skills))
