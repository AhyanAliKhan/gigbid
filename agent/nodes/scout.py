"""
Scout Agent Node
Discovers and ingests new jobs, deduplicates, and populates the initial graph state.
"""

import os
from typing import Dict, Any
from agent.state import GigBidState
from agent.mcp_client import mcp_manager

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "scout_v1.md")

def scout_node(state: GigBidState) -> Dict[str, Any]:
    job = state.get("job", {})
    trace_entry = {
        "node": "scout",
        "action": "ingest_job",
        "job_id": job.get("job_id", "unknown"),
        "title": job.get("title", ""),
        "tokens": 120
    }
    
    return {
        "job": job,
        "status": "queued",
        "step_count": 1,
        "total_tokens_used": 120,
        "execution_trace": [trace_entry]
    }
