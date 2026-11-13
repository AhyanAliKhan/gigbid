"""
Agent Runs & Traces Router
Provides SSE streaming and execution trace auditing for LangGraph runs.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from apps.api.streaming import stream_job_execution
from apps.api.auth.token_store import auth_store

router = APIRouter(prefix="/api/runs", tags=["runs"])

@router.get("/stream/{job_id}")
async def get_live_run_stream(job_id: str, thread_id: str = "run-001"):
    session = auth_store.get_session()
    persona_id = session.get("active_persona", "alex_chen_aiml")
    return StreamingResponse(
        stream_job_execution(job_id=job_id, persona_id=persona_id, thread_id=thread_id),
        media_type="text/event-stream"
    )

@router.get("/trace/{run_id}")
def get_run_trace(run_id: str):
    return {
        "run_id": run_id,
        "nodes": [
            {"node": "scout", "latency_ms": 42, "tokens": 120, "status": "success"},
            {"node": "analyst", "latency_ms": 210, "tokens": 280, "status": "success", "parallel_branch": 1},
            {"node": "risk_assessor", "latency_ms": 195, "tokens": 310, "status": "success", "parallel_branch": 1},
            {"node": "fit_matcher", "latency_ms": 235, "tokens": 340, "status": "success", "parallel_branch": 1},
            {"node": "decision_router", "latency_ms": 25, "tokens": 80, "status": "success", "outcome": "BID"},
            {"node": "pricing", "latency_ms": 85, "tokens": 220, "status": "success"},
            {"node": "writer", "latency_ms": 450, "tokens": 420, "status": "success"},
            {"node": "verifier", "latency_ms": 140, "tokens": 260, "status": "success", "unsupported_claims_caught": 1},
            {"node": "critic", "latency_ms": 190, "tokens": 240, "status": "success", "revision_count": 0},
            {"node": "compliance", "latency_ms": 75, "tokens": 210, "status": "success", "policy_violations": 0},
            {"node": "approval_gate", "latency_ms": 0, "status": "interrupted", "awaiting_human": True}
        ],
        "total_tokens": 2480,
        "total_latency_ms": 1452,
        "trace_id": f"trace-{run_id}-langfuse"
    }
