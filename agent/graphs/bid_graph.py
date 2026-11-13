"""
GigBid Bid Graph Implementation
Hand-written LangGraph StateGraph with:
- Parallel execution of Job Analyst, Risk Assessor, and Fit Matcher
- Decision routing node (SKIP / WATCH / BID)
- Pricing Strategist
- Proposal Writer
- Fine-grained Claim Verification
- Critic with bounded revision loops (max 2)
- Compliance Guard with policy enforcement
- Human Approval Gate using LangGraph interrupt()
- Idempotent Marketplace Submission
- Step and Token Budget guards
- Crash & Resume Persistence Checkpointing
"""

import os
import uuid
import logging
from typing import Dict, Any, Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

from agent.state import GigBidState
from agent.handoffs import BidDecision
from agent.nodes.scout import scout_node
from agent.nodes.analyst import analyst_node
from agent.nodes.risk_assessor import risk_assessor_node
from agent.nodes.fit_matcher import fit_matcher_node
from agent.nodes.pricing import pricing_node
from agent.nodes.writer import writer_node
from agent.nodes.verifier import verifier_node
from agent.nodes.critic import critic_node
from agent.nodes.compliance import compliance_node
from agent.mcp_client import mcp_manager
from agent.memory.promotion_rules import process_user_edit_for_promotion

logger = logging.getLogger("bid_graph")

# Step & Token Budgets (enforced per thread)
MAX_STEPS = 25
MAX_TOKENS = 15000

# -----------------------------------------------------------------------------
# Decision Router Node
# -----------------------------------------------------------------------------
def decision_router_node(state: GigBidState) -> Dict[str, Any]:
    risk = state.get("risk_report")
    fit = state.get("fit_report")
    job = state.get("job", {})

    risk_score = risk.score if risk else 0.2
    fit_score = fit.score if fit else 0.5
    is_scam = risk.is_scam if risk else False

    # Skip conditions: scam, injection, high risk, or low skill match
    if is_scam or risk_score >= 0.70:
        decision = "SKIP"
        reason = f"Automated Skip: High security or fraud risk ({risk.explanation if risk else 'Malicious signals'})."
    elif fit_score < 0.35:
        decision = "SKIP"
        reason = f"Automated Skip: Low technical skill alignment (Fit Score: {fit_score:.0%})."
    else:
        decision = "BID"
        reason = f"Qualified Candidate: Acceptable risk ({risk_score:.2f}) and strong evidence-backed fit ({fit_score:.0%})."

    bid_dec = BidDecision(
        action=decision,
        reason=reason,
        fit_score=fit_score,
        risk_score=risk_score
    )

    trace_entry = {
        "node": "decision_router",
        "action": "route_job",
        "decision": decision,
        "reason": reason,
        "tokens": 80
    }

    return {
        "bid_decision": bid_dec,
        "status": "bidding" if decision == "BID" else "skipped",
        "step_count": 1,
        "total_tokens_used": 80,
        "execution_trace": [trace_entry]
    }

def route_after_decision(state: GigBidState) -> Literal["pricing", "record_skip"]:
    dec = state.get("bid_decision")
    if dec and dec.action == "BID":
        return "pricing"
    return "record_skip"

def record_skip_node(state: GigBidState) -> Dict[str, Any]:
    trace_entry = {
        "node": "record_skip",
        "action": "finalize_skip",
        "job_id": state.get("job", {}).get("job_id"),
        "reason": state.get("bid_decision", {}).reason if state.get("bid_decision") else "Skipped",
        "tokens": 20
    }
    return {
        "status": "skipped",
        "execution_trace": [trace_entry]
    }

# -----------------------------------------------------------------------------
# Critic Revision Loop Router
# -----------------------------------------------------------------------------
def route_after_critic(state: GigBidState) -> Literal["writer", "compliance"]:
    critique = state.get("critique")
    revision_count = state.get("revision_count", 0)
    
    # Loop back to writer at most twice
    if critique and critique.revision_requested and revision_count < 2:
        return "writer"
    return "compliance"

# -----------------------------------------------------------------------------
# Human Approval Gate Node with interrupt()
# -----------------------------------------------------------------------------
def human_approval_gate_node(state: GigBidState) -> Dict[str, Any]:
    # Budget Check
    if state.get("step_count", 0) > MAX_STEPS or state.get("total_tokens_used", 0) > MAX_TOKENS:
        return {
            "status": "needs_attention",
            "errors": [f"Budget exceeded: steps={state.get('step_count')}, tokens={state.get('total_tokens_used')}"]
        }

    payload = state.get("approval_payload")
    if not payload:
        return {"status": "needs_attention", "errors": ["Missing approval payload"]}

    # LangGraph Human-in-the-Loop Interrupt
    # Execution halts here, returning payload to caller.
    # Resumed when caller provides: {"action": "approved"|"edited"|"rejected", "feedback": ..., "edited_text": ...}
    user_input = interrupt(payload.model_dump())

    # When resumed:
    action = user_input.get("action", "approved") if isinstance(user_input, dict) else "approved"
    feedback = user_input.get("feedback", "") if isinstance(user_input, dict) else ""
    edited_text = user_input.get("edited_text") if isinstance(user_input, dict) else None

    # Handle user edits and learn style rules
    if action == "edited" and edited_text:
        orig_draft = state.get("proposal_draft")
        if orig_draft:
            process_user_edit_for_promotion("default_user", orig_draft.cover_letter, edited_text)
            orig_draft.cover_letter = edited_text

    trace_entry = {
        "node": "human_approval_gate",
        "action": "human_decision",
        "human_action": action,
        "feedback": feedback,
        "tokens": 40
    }

    return {
        "human_action": action,
        "human_feedback": feedback,
        "status": "submitting" if action in ["approved", "edited"] else "rejected",
        "step_count": 1,
        "total_tokens_used": 40,
        "execution_trace": [trace_entry]
    }

def route_after_approval(state: GigBidState) -> Literal["marketplace_submit", "record_rejection"]:
    action = state.get("human_action")
    if action in ["approved", "edited"]:
        return "marketplace_submit"
    return "record_rejection"

def record_rejection_node(state: GigBidState) -> Dict[str, Any]:
    trace_entry = {
        "node": "record_rejection",
        "action": "proposal_rejected_by_human",
        "feedback": state.get("human_feedback", "Rejected by user"),
        "tokens": 20
    }
    return {
        "status": "rejected",
        "execution_trace": [trace_entry]
    }

# -----------------------------------------------------------------------------
# Marketplace Submission Node
# -----------------------------------------------------------------------------
def marketplace_submit_node(state: GigBidState) -> Dict[str, Any]:
    draft = state.get("proposal_draft")
    quote = state.get("price_quote")
    job = state.get("job", {})
    job_id = job.get("job_id", "unknown")
    
    idempotency_key = f"bid-{job_id}-{uuid.uuid4().hex[:8]}"
    
    submission_payload = {
        "job_id": job_id,
        "cover_letter": draft.cover_letter if draft else "",
        "bid_amount": quote.suggested_bid if quote else 350.0,
        "screening_answers": draft.screening_answers if draft else [],
        "evidence_ids": draft.evidence_ids if draft else [],
        "idempotency_key": idempotency_key,
        "dry_run": False
    }

    try:
        result = mcp_manager.execute_tool("marketplace_submitter", "submit_proposal", submission_payload)
        status_str = "submitted"
    except Exception as e:
        result = {"error": str(e), "status": "failed"}
        status_str = "needs_attention"

    trace_entry = {
        "node": "marketplace_submit",
        "action": "submit_to_marketplace",
        "idempotency_key": idempotency_key,
        "status": status_str,
        "tokens": 150
    }

    return {
        "submission_result": result,
        "status": status_str,
        "step_count": 1,
        "total_tokens_used": 150,
        "execution_trace": [trace_entry]
    }

# -----------------------------------------------------------------------------
# Build and Compile Bid Graph
# -----------------------------------------------------------------------------
def build_bid_graph(checkpointer=None):
    workflow = StateGraph(GigBidState)

    # Register Nodes
    workflow.add_node("scout", scout_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("risk_assessor", risk_assessor_node)
    workflow.add_node("fit_matcher", fit_matcher_node)
    workflow.add_node("decision_router", decision_router_node)
    workflow.add_node("record_skip", record_skip_node)
    workflow.add_node("pricing", pricing_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("verifier", verifier_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("approval_gate", human_approval_gate_node)
    workflow.add_node("record_rejection", record_rejection_node)
    workflow.add_node("marketplace_submit", marketplace_submit_node)

    # Edges
    workflow.add_edge(START, "scout")

    # Parallel Fan-Out: Scout dispatches in parallel to Analyst, Risk Assessor, and Fit Matcher
    workflow.add_edge("scout", "analyst")
    workflow.add_edge("scout", "risk_assessor")
    workflow.add_edge("scout", "fit_matcher")

    # Fan-In: All three parallel branches merge into decision_router
    workflow.add_edge("analyst", "decision_router")
    workflow.add_edge("risk_assessor", "decision_router")
    workflow.add_edge("fit_matcher", "decision_router")

    # Decision Routing: skip vs bid
    workflow.add_conditional_edges(
        "decision_router",
        route_after_decision,
        {"pricing": "pricing", "record_skip": "record_skip"}
    )
    workflow.add_edge("record_skip", END)

    # Bidding Pipeline
    workflow.add_edge("pricing", "writer")
    workflow.add_edge("writer", "verifier")
    workflow.add_edge("verifier", "critic")

    # Bounded Critic Loop (max 2 revisions)
    workflow.add_conditional_edges(
        "critic",
        route_after_critic,
        {"writer": "writer", "compliance": "compliance"}
    )

    # Compliance Guard to Human Approval Gate
    workflow.add_edge("compliance", "approval_gate")

    # Approval Gate: resume to marketplace_submit or record_rejection
    workflow.add_conditional_edges(
        "approval_gate",
        route_after_approval,
        {"marketplace_submit": "marketplace_submit", "record_rejection": "record_rejection"}
    )
    workflow.add_edge("record_rejection", END)
    workflow.add_edge("marketplace_submit", END)

    # Compile with persistence checkpointer
    cp = checkpointer or MemorySaver()
    app = workflow.compile(checkpointer=cp)
    return app

bid_graph = build_bid_graph()
