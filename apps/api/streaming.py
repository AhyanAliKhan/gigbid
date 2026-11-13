"""
Server-Sent Events (SSE) Streaming Bridge
Streams LangGraph node execution events, token progress, and approval gates to the frontend.
"""

import json
import asyncio
from typing import AsyncGenerator, Dict, Any
from fastapi.responses import StreamingResponse
from langgraph.types import Command
from agent.graphs.bid_graph import build_bid_graph
from gigsim.server import get_job

# Shared checkpointer and global registry of active runs for streaming
ACTIVE_RUN_THREADS: Dict[str, Dict[str, Any]] = {}

async def stream_job_execution(job_id: str, persona_id: str, thread_id: str) -> AsyncGenerator[str, None]:
    """Streams live LangGraph node-by-node execution events."""
    try:
        job = get_job(job_id)
    except Exception:
        yield f"data: {json.dumps({'event': 'error', 'message': f'Job {job_id} not found'})}\n\n"
        return

    graph = build_bid_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    yield f"data: {json.dumps({'event': 'start', 'job_id': job_id, 'thread_id': thread_id})}\n\n"
    await asyncio.sleep(0.05)

    try:
        # Stream updates from LangGraph
        for chunk in graph.stream({"job": job, "persona_id": persona_id}, config=config):
            for node_name, node_update in chunk.items():
                event_payload = {
                    "event": "node_complete",
                    "node": node_name,
                    "status": node_update.get("status", "running"),
                    "tokens_used": node_update.get("total_tokens_used", 0),
                    "step_count": node_update.get("step_count", 1)
                }
                # If approval gate reached
                if "approval_payload" in node_update and node_update["approval_payload"]:
                    event_payload["event"] = "waiting_approval"
                    event_payload["approval_payload"] = node_update["approval_payload"].model_dump()
                
                # If skipped
                if node_name == "decision_router" and node_update.get("status") == "skipped":
                    event_payload["event"] = "job_skipped"
                    event_payload["reason"] = node_update.get("bid_decision", {}).reason if hasattr(node_update.get("bid_decision"), "reason") else "Low fit or high risk."

                yield f"data: {json.dumps(event_payload)}\n\n"
                await asyncio.sleep(0.1)

    except Exception as e:
        yield f"data: {json.dumps({'event': 'error', 'detail': str(e)})}\n\n"

    yield f"data: {json.dumps({'event': 'stream_end', 'thread_id': thread_id})}\n\n"
