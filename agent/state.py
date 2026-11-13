"""
GigBid LangGraph Typed State Design
Enforces strict separation of three concerns:
1. State: what this job or conversation needs right now to execute.
2. Execution Trace: append-only log of every node, tool call, argument, result, and token count.
3. Long-Term Memory: persistent promoted knowledge in LangGraph Store, updated only via explicit rules.
Includes reducers for parallel branch fan-in (Analyst, Risk Assessor, Fit Matcher).
"""

import operator
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from agent.handoffs import (
    JobSpec,
    RiskReport,
    FitReport,
    BidDecision,
    PriceQuote,
    ProposalDraft,
    Critique,
    ComplianceVerdict,
    ApprovalPayload
)

def reduce_dict(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Reducer combining dictionary updates from parallel branches."""
    merged = dict(left or {})
    merged.update(right or {})
    return merged

def reduce_list(left: List[Any], right: List[Any]) -> List[Any]:
    """Reducer appending items from parallel branches."""
    return list(left or []) + list(right or [])

def reduce_last(left: Any, right: Any) -> Any:
    """Reducer picking the latest non-None value."""
    return right if right is not None else left

class GigBidState(TypedDict, total=False):
    # -------------------------------------------------------------
    # 1. Active Working State
    # -------------------------------------------------------------
    job: Dict[str, Any]
    persona_id: str
    
    # Parallel analysis branch outputs (merged via reducers)
    analyses: Annotated[Dict[str, Any], reduce_dict]
    job_spec: Optional[JobSpec]
    risk_report: Optional[RiskReport]
    fit_report: Optional[FitReport]
    
    # Retrieval & decisions
    retrieved_evidence: List[Dict[str, Any]]
    bid_decision: Optional[BidDecision]
    price_quote: Optional[PriceQuote]
    
    # Drafting & verification
    proposal_draft: Optional[ProposalDraft]
    claim_verification: Optional[Dict[str, Any]]
    critique: Optional[Critique]
    compliance_verdict: Optional[ComplianceVerdict]
    
    # Human-in-the-loop approval gate
    approval_payload: Optional[ApprovalPayload]
    human_action: Optional[str] # "approved", "edited", "rejected"
    human_feedback: Optional[str]
    edited_draft_text: Optional[str]
    
    # Submission outcome
    submission_result: Optional[Dict[str, Any]]
    
    # Budgets & loop counters (with reducers for concurrent parallel execution)
    step_count: Annotated[int, operator.add]
    revision_count: Annotated[int, reduce_last]
    total_tokens_used: Annotated[int, operator.add]
    status: Annotated[str, reduce_last] # "queued", "analyzing", "bidding", "skipped", "waiting_approval", "submitted", "needs_attention"
    
    # -------------------------------------------------------------
    # 2. Execution Trace (Audit, Observability & Debugging)
    # -------------------------------------------------------------
    execution_trace: Annotated[List[Dict[str, Any]], reduce_list]
    errors: Annotated[List[str], reduce_list]

class ConversationState(TypedDict, total=False):
    thread_id: str
    client_id: str
    incoming_message: Dict[str, Any]
    classified_intent: str # "question", "negotiation", "interview_request", "scam_signal"
    intent_confidence: float
    calendar_slots: List[Dict[str, Any]]
    draft_response: str
    human_approved: bool
    sent_result: Dict[str, Any]
    trace: Annotated[List[Dict[str, Any]], reduce_list]
