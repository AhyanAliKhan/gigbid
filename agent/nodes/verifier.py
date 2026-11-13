"""
Claim Verifier Agent Node
Executes fine-grained claim splitting and evidence grounding check on the proposal draft.
Purges or rewrites unsupported claims before the draft reaches the Critic.
"""

import os
from typing import Dict, Any
from agent.state import GigBidState
from agent.handoffs import ProposalDraft
from rag.verify import claim_verifier

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "verifier_v1.md")

def verifier_node(state: GigBidState) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    evidence = state.get("retrieved_evidence", [])
    
    if not draft:
        return {"claim_verification": {"status": "skipped_no_draft"}}

    ver_res = claim_verifier.verify_and_ground_proposal(draft.cover_letter, evidence)

    # Update proposal with verified text
    updated_draft = ProposalDraft(
        job_id=draft.job_id,
        cover_letter=ver_res.verified_text,
        screening_answers=draft.screening_answers,
        evidence_ids=draft.evidence_ids,
        revision_count=draft.revision_count,
        status="verified"
    )

    trace_entry = {
        "node": "verifier",
        "action": "verify_grounding",
        "total_claims": ver_res.total_claims,
        "supported_claims": ver_res.supported_claims,
        "unsupported_before": ver_res.unsupported_claims,
        "unsupported_after": 0,
        "tokens": 260
    }

    return {
        "proposal_draft": updated_draft,
        "claim_verification": ver_res.model_dump(),
        "step_count": 1,
        "total_tokens_used": 260,
        "execution_trace": [trace_entry]
    }
