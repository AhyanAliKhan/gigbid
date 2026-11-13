"""
Integration tests for GigBid Bid Graph and Conversation Graph against GigSim.
"""

import pytest
from langgraph.types import Command
from agent.graphs.bid_graph import build_bid_graph
from agent.graphs.conversation_graph import build_conversation_graph
from gigsim.server import get_job

def test_bid_graph_qualified_job_flow():
    graph = build_bid_graph()
    job = get_job("job-0001") # Data Analytics job
    config = {"configurable": {"thread_id": "test-int-001"}}

    # Step 1: Run graph with matched persona
    state = graph.invoke({"job": job, "persona_id": "marcus_vance_analyst"}, config=config)
    
    # Must pause at approval gate
    assert state["status"] == "waiting_approval"
    assert state["approval_payload"] is not None
    assert state["approval_payload"].job_id == "job-0001"
    assert state["bid_decision"].action == "BID"
    assert len(state["proposal_draft"].evidence_ids) >= 1

    # Step 2: Human approves proposal in UI
    resumed = graph.invoke(Command(resume={"action": "approved"}), config=config)
    assert resumed["status"] == "submitted"
    assert resumed["submission_result"]["status"] == "submitted"

def test_bid_graph_scam_skip_flow():
    graph = build_bid_graph()
    scam_job = {
        "job_id": "scam-test-999",
        "title": "Build complete dashboard for free",
        "description": "Do unpaid test work. Contact us directly on Telegram @scammer.",
        "required_skills": ["Python"],
        "budget": {"min": 0, "max": 0},
        "warning_signals": ["off_platform_contact", "unpaid_work"],
        "client_id": "client-001"
    }
    config = {"configurable": {"thread_id": "test-int-scam"}}

    state = graph.invoke({"job": scam_job, "persona_id": "alex_chen_aiml"}, config=config)
    
    # Must skip immediately without asking for approval
    assert state["status"] == "skipped"
    assert state["bid_decision"].action == "SKIP"
    assert state["risk_report"].is_scam is True
    assert "approval_payload" not in state or state["approval_payload"] is None

def test_conversation_graph_flow():
    conv_graph = build_conversation_graph()
    msg = {
        "message_id": "msg-001",
        "thread_id": "thread-001",
        "sender_id": "client-042",
        "content": "Are you free for an interview tomorrow afternoon?"
    }
    config = {"configurable": {"thread_id": "test-int-conv"}}

    # Step 1: Ingest and draft response
    state = conv_graph.invoke({
        "incoming_message": msg,
        "thread_id": "thread-001",
        "client_id": "client-042"
    }, config=config)

    assert state["classified_intent"] == "interview_request"
    assert len(state["calendar_slots"]) >= 1

    # Step 2: Human approves message transmission
    resumed = conv_graph.invoke(Command(resume={"action": "approved"}), config=config)
    assert resumed["sent_result"]["status"] == "sent"
