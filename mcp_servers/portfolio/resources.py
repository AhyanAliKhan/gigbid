"""
Portfolio MCP Server Resources
Provides URI-based resource templates for loading full case studies and proposals.
"""

import os
import json
from typing import Optional
from mcp_servers.portfolio.tools import load_persona_data, get_active_persona_id

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PERSONAS_DIR = os.path.join(BASE_DIR, "data", "personas")

def read_case_resource(id: str) -> str:
    """Resource template: portfolio://case/{id}"""
    pid = get_active_persona_id()
    md_path = os.path.join(PERSONAS_DIR, pid, "case_studies", f"{id}.md")
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read()
    data = load_persona_data(pid)
    for cs in data["case_studies"]:
        if cs["id"].lower() == id.lower():
            return json.dumps(cs, indent=2)
    return f"Case study '{id}' not found for persona '{pid}'."

def read_proposal_resource(id: str) -> str:
    """Resource template: portfolio://proposal/{id}"""
    pid = get_active_persona_id()
    data = load_persona_data(pid)
    for p in data["past_proposals"]:
        if p["proposal_id"].lower() == id.lower():
            return json.dumps(p, indent=2)
    return f"Proposal '{id}' not found for persona '{pid}'."
