"""
Job Analyst Agent Node
Extracts structured JobSpec from raw untrusted job posting text.
Runs in parallel with Risk Assessor and Fit Matcher.
Tool Access: None (enforced by MCP manager client discipline).
"""

import os
import re
from typing import Dict, Any
from agent.state import GigBidState
from agent.handoffs import JobSpec

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "analyst_v1.md")

def analyst_node(state: GigBidState) -> Dict[str, Any]:
    job = state.get("job", {})
    desc = job.get("description", "")
    title = job.get("title", "")
    
    # Extract deliverables
    deliverables = []
    for line in desc.split("."):
        clean = line.strip()
        if any(kw in clean.lower() for kw in ["build", "create", "implement", "deploy", "design", "develop", "model", "refactor"]):
            deliverables.append(clean[:120])
    if not deliverables:
        deliverables.append(f"Deliver production-grade solution for {title}")

    # Skills
    skills = job.get("required_skills", [])
    if not skills:
        skills = [w for w in ["Python", "FastAPI", "React", "PostgreSQL", "PyTorch", "Docker"] if w.lower() in desc.lower()]

    spec = JobSpec(
        job_id=job.get("job_id", "unknown"),
        title=title,
        deliverables=deliverables[:4],
        required_skills=skills,
        budget_min=job.get("budget", {}).get("min"),
        budget_max=job.get("budget", {}).get("max"),
        timeline_days=job.get("duration_days", 14),
        screening_questions=job.get("screening_questions", []),
        hidden_needs=["High availability", "Test coverage >90%", "Strict data privacy"]
    )

    trace_entry = {
        "node": "analyst",
        "action": "extract_job_spec",
        "deliverables_count": len(spec.deliverables),
        "skills_count": len(spec.required_skills),
        "tokens": 280
    }

    return {
        "job_spec": spec,
        "analyses": {"analyst": spec.model_dump()},
        "step_count": 1,
        "total_tokens_used": 280,
        "execution_trace": [trace_entry]
    }
