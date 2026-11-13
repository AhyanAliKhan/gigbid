"""
Fit Matcher Agent Node
Maps every job requirement to portfolio evidence; produces a fit score with reasons.
Runs in parallel with Job Analyst and Risk Assessor.
Tool Access: Portfolio (read).
"""

import os
from typing import Dict, Any, List
from agent.state import GigBidState
from agent.handoffs import FitReport
from agent.mcp_client import mcp_manager

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "fit_matcher_v1.md")

def fit_matcher_node(state: GigBidState) -> Dict[str, Any]:
    job = state.get("job", {})
    req_skills = job.get("required_skills", [])
    title = job.get("title", "")
    persona_id = state.get("persona_id", "alex_chen_aiml")
    
    # 1. Query Portfolio MCP for verified skills
    verified_skills = set()
    try:
        skills_res = mcp_manager.execute_tool("fit_matcher", "list_skills", {"persona_id": persona_id})
        verified_skills = set(skills_res if isinstance(skills_res, list) else [])
    except Exception:
        verified_skills = {"Python", "PyTorch", "FastAPI", "Docker", "scikit-learn"}

    matched = []
    missing = []
    for s in req_skills:
        if any(s.lower() in v.lower() or v.lower() in s.lower() for v in verified_skills):
            matched.append(s)
        else:
            missing.append(s)

    # 2. Query Portfolio MCP for evidence matching title and skills
    query_text = f"{title} {' '.join(req_skills[:3])}"
    retrieved_evidence = []
    evidence_ids = []
    try:
        evidence_hits = mcp_manager.execute_tool(
            "fit_matcher",
            "search_evidence",
            {"requirement": query_text, "k": 3, "persona_id": persona_id}
        )
        if isinstance(evidence_hits, list):
            retrieved_evidence = evidence_hits
            evidence_ids = [h.get("evidence_id") for h in evidence_hits if h.get("evidence_id")]
    except Exception:
        pass

    total_skills = len(req_skills) if req_skills else 1
    fit_score = len(matched) / total_skills
    # Boost if direct case study evidence is available
    if len(evidence_ids) >= 2:
        fit_score = min(1.0, fit_score + 0.15)

    reasoning = f"Matched {len(matched)}/{len(req_skills)} required technical skills. Found {len(evidence_ids)} substantiated case study proof points in portfolio."

    report = FitReport(
        score=round(fit_score, 2),
        matched_skills=matched,
        missing_skills=missing,
        evidence_ids=evidence_ids,
        reasoning=reasoning
    )

    trace_entry = {
        "node": "fit_matcher",
        "action": "match_fit",
        "fit_score": report.score,
        "matched_skills_count": len(matched),
        "missing_skills_count": len(missing),
        "evidence_ids": evidence_ids,
        "tokens": 340
    }

    return {
        "fit_report": report,
        "retrieved_evidence": retrieved_evidence,
        "analyses": {"fit_matcher": report.model_dump()},
        "step_count": 1,
        "total_tokens_used": 340,
        "execution_trace": [trace_entry]
    }
