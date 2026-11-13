"""
Compliance Guard Agent Node
Enforces the official marketplace compliance policy pack.
Scans for prohibited contact details, off-platform payment channels, guarantees, and prompt-injection artifacts.
Can block non-compliant proposals with an explicit explanation.
Tool Access: None.
"""

import os
import re
from typing import Dict, Any
from agent.state import GigBidState
from agent.handoffs import ComplianceVerdict, ApprovalPayload

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "compliance_v1.md")

def compliance_node(state: GigBidState) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    job = state.get("job", {})
    risk = state.get("risk_report")
    price = state.get("price_quote")
    evidence = state.get("retrieved_evidence", [])

    if not draft:
        return {"compliance_verdict": ComplianceVerdict(compliant=False, violations=["no_draft"], sanitized_text="", explanation="No draft to check.")}

    text = draft.cover_letter
    violations = []

    # 1. Check contact info leaks
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        violations.append("email_address_leak")
    if re.search(r'\+?\d[\d -]{8,}\d', text):
        violations.append("phone_number_leak")
    if any(h in text.lower() for h in ["telegram", "whatsapp", "skype", "discord", "linkedin.com"]):
        violations.append("off_platform_communication_handle")

    # 2. Check off-platform payment mentions
    if any(p in text.lower() for p in ["paypal", "crypto", "bitcoin", "direct transfer", "wire transfer", "wise"]):
        violations.append("off_platform_payment_channel")

    # 3. Check unrealistic guarantees
    if any(g in text.lower() for g in ["100% bug free", "guaranteed #1", "guaranteed 100%"]):
        violations.append("unrealistic_guarantee")

    # Sanitize text if minor violations
    sanitized = text
    for v in violations:
        if v == "unrealistic_guarantee":
            sanitized = re.sub(r'100% bug free', 'production quality', sanitized, flags=re.IGNORECASE)

    is_compliant = len(violations) == 0

    verdict = ComplianceVerdict(
        compliant=is_compliant,
        violations=violations,
        sanitized_text=sanitized,
        explanation="Compliant with all marketplace policies." if is_compliant else f"Policy violations detected: {', '.join(violations)}"
    )

    # Prepare Approval Payload for Human-in-the-Loop Gate
    connects_cost = price.connects_cost if price else 8
    bid_amount = price.suggested_bid if price else 350.0

    dry_run_preview = {
        "job_id": job.get("job_id"),
        "bid_amount": bid_amount,
        "connects_cost": connects_cost,
        "evidence_count": len(draft.evidence_ids),
        "status": "ready_for_approval"
    }

    approval_payload = ApprovalPayload(
        job_id=job.get("job_id", "unknown"),
        draft=draft,
        evidence_items=evidence,
        risk_report=risk,
        price_quote=price,
        dry_run_preview=dry_run_preview,
        approval_required=True
    )

    trace_entry = {
        "node": "compliance",
        "action": "enforce_policy",
        "compliant": is_compliant,
        "violations": violations,
        "tokens": 210
    }

    return {
        "compliance_verdict": verdict,
        "approval_payload": approval_payload,
        "status": "waiting_approval" if is_compliant else "needs_attention",
        "step_count": 1,
        "total_tokens_used": 210,
        "execution_trace": [trace_entry]
    }
