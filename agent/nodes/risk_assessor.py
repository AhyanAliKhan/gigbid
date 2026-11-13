"""
Risk Assessor Agent Node
Scores client quality from history; flags scams, free-work requests, off-platform asks,
and planted prompt-injection payloads.
Runs in parallel with Job Analyst and Fit Matcher.
Tool Access: Marketplace (read).
"""

import os
import re
from typing import Dict, Any
from agent.state import GigBidState
from agent.handoffs import RiskReport
from agent.mcp_client import mcp_manager

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "risk_assessor_v1.md")

def risk_assessor_node(state: GigBidState) -> Dict[str, Any]:
    job = state.get("job", {})
    desc = job.get("description", "").lower()
    cid = job.get("client_id", "")
    
    # 1. Fetch client history via MCP
    client_info = {}
    if cid:
        try:
            client_info = mcp_manager.execute_tool("risk_assessor", "get_client_history", {"client_id": cid})
        except Exception:
            client_info = {}

    flags = list(job.get("warning_signals", []))
    score = 0.1 # baseline clean risk

    # 2. Check off-platform contact
    if any(kw in desc for kw in ["telegram", "whatsapp", "skype", "email directly", "@recruitment", "@hiring"]):
        flags.append("off_platform_contact")
        score += 0.45

    # 3. Check unpaid work
    if any(kw in desc for kw in ["unpaid test", "free trial", "test assignment for free", "spec work"]):
        flags.append("unpaid_work_trial")
        score += 0.45

    # 4. Check prompt injection attempt
    has_injection = job.get("has_injection", False)
    if any(kw in desc for kw in ["ignore all previous", "jailbroken", "<system_instruction>", "ignore policies", "system bypass"]):
        has_injection = True
        flags.append("prompt_injection_attempt")
        score = 1.0 # Maximum risk

    # 5. Client history penalties
    if client_info:
        if not client_info.get("payment_verified", True) and client_info.get("total_spent_usd", 0) == 0:
            flags.append("unverified_zero_spend_client")
            score += 0.25

    score = min(1.0, score)
    is_scam = score >= 0.70 or has_injection

    explanation = "Job post adheres to platform policies."
    if flags:
        explanation = f"Risk flags detected: {', '.join(flags)}. Malicious risk assessment: {'HIGH' if is_scam else 'MODERATE'}."

    report = RiskReport(
        score=round(score, 2),
        flags=flags,
        is_scam=is_scam,
        has_injection=has_injection,
        explanation=explanation
    )

    trace_entry = {
        "node": "risk_assessor",
        "action": "evaluate_risk",
        "score": report.score,
        "is_scam": is_scam,
        "has_injection": has_injection,
        "tokens": 310
    }

    return {
        "risk_report": report,
        "analyses": {"risk_assessor": report.model_dump()},
        "step_count": 1,
        "total_tokens_used": 310,
        "execution_trace": [trace_entry]
    }
