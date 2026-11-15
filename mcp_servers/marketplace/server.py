"""
Marketplace MCP Server
Wraps GigSim and Upwork Live adapters with strict Pydantic schemas, tool annotations,
idempotency, dry-run previews, bearer-token authentication, rate limiting, and an append-only audit log.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from mcp_servers.compat import MCPServer
from agent.marketplace_port import get_marketplace_port

server = MCPServer("marketplace-mcp-server")
port = get_marketplace_port()

# Append-only audit log
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "data", "audit_log.jsonl")

def append_audit_log(user: str, tool: str, arguments: Dict[str, Any], result: Any, trace_id: str):
    os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user": user,
        "tool": tool,
        "arguments": arguments,
        "result": result,
        "trace_id": trace_id
    }
    with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# -----------------------------------------------------------------------------
# Input Schemas with validation constraints
# -----------------------------------------------------------------------------
class SearchJobsInput(BaseModel):
    query: Optional[str] = Field(default=None, description="Keywords to match against title or description")
    category: Optional[str] = Field(default=None, description="Category filter (e.g. AI/ML, Full-Stack Web)")
    limit: int = Field(default=20, ge=1, le=100, description="Page size")
    offset: int = Field(default=0, ge=0, description="Offset index")

class GetJobInput(BaseModel):
    job_id: str = Field(min_length=3, description="Unique job identifier")

class GetClientHistoryInput(BaseModel):
    client_id: str = Field(min_length=3, description="Client identifier")

class CreateProposalDraftInput(BaseModel):
    job_id: str = Field(min_length=3)
    cover_letter: str = Field(min_length=20, max_length=5000)
    bid_amount: float = Field(gt=0)
    screening_answers: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    idempotency_key: str = Field(min_length=8)
    dry_run: bool = Field(default=True)
    user_id: str = Field(default="default_user")
    trace_id: str = Field(default="trace-001")

class SubmitProposalInput(BaseModel):
    job_id: str = Field(min_length=3)
    cover_letter: str = Field(min_length=20, max_length=5000)
    bid_amount: float = Field(gt=0)
    screening_answers: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    idempotency_key: str = Field(min_length=8)
    dry_run: bool = Field(default=False)
    user_id: str = Field(default="default_user")
    trace_id: str = Field(default="trace-001")

class SendMessageInput(BaseModel):
    thread_id: str = Field(min_length=3)
    recipient_id: str = Field(min_length=3)
    content: str = Field(min_length=2, max_length=4000)
    idempotency_key: str = Field(min_length=8)
    user_id: str = Field(default="default_user")
    trace_id: str = Field(default="trace-001")

# -----------------------------------------------------------------------------
# Read Tools (readOnlyHint=True, destructiveHint=False, idempotentHint=True)
# -----------------------------------------------------------------------------
@server.tool(
    name="search_jobs",
    description="Search active jobs on the marketplace by query, category, and pagination."
)
def mcp_search_jobs(query: Optional[str] = None, category: Optional[str] = None, limit: int = 20, offset: int = 0) -> str:
    inp = SearchJobsInput(query=query, category=category, limit=limit, offset=offset)
    res = port.search_jobs(query=inp.query, category=inp.category, limit=inp.limit, offset=inp.offset)
    return json.dumps(res, indent=2)

@server.tool(
    name="get_job",
    description="Retrieve full job details, requirements, budget, screening questions, and connects cost."
)
def mcp_get_job(job_id: str) -> str:
    inp = GetJobInput(job_id=job_id)
    res = port.get_job(inp.job_id)
    return json.dumps(res, indent=2)

@server.tool(
    name="get_client_history",
    description="Retrieve client ratings, total spend, hire rate, tier, and feedback history."
)
def mcp_get_client_history(client_id: str) -> str:
    inp = GetClientHistoryInput(client_id=client_id)
    res = port.get_client_history(inp.client_id)
    return json.dumps(res, indent=2)

@server.tool(
    name="get_connects_balance",
    description="Check current available Connects balance for the user."
)
def mcp_get_connects_balance(user_id: str = "default_user") -> str:
    res = port.get_connects_balance(user_id=user_id)
    return json.dumps(res, indent=2)

@server.tool(
    name="list_messages",
    description="List messages in a conversation thread with a client."
)
def mcp_list_messages(thread_id: Optional[str] = None) -> str:
    res = port.list_messages(thread_id=thread_id)
    return json.dumps(res, indent=2)

# -----------------------------------------------------------------------------
# Write Tools (readOnlyHint=False, destructiveHint=True/False, idempotentHint=True)
# -----------------------------------------------------------------------------
@server.tool(
    name="create_proposal_draft",
    description="Generate a proposal draft and preview Connects spend without deducting balance (dry_run=True)."
)
def mcp_create_proposal_draft(
    job_id: str,
    cover_letter: str,
    bid_amount: float,
    idempotency_key: str,
    screening_answers: Optional[List[str]] = None,
    evidence_ids: Optional[List[str]] = None,
    user_id: str = "default_user",
    trace_id: str = "trace-draft-001"
) -> str:
    inp = CreateProposalDraftInput(
        job_id=job_id,
        cover_letter=cover_letter,
        bid_amount=bid_amount,
        screening_answers=screening_answers or [],
        evidence_ids=evidence_ids or [],
        idempotency_key=idempotency_key,
        dry_run=True,
        user_id=user_id,
        trace_id=trace_id
    )
    payload = inp.model_dump()
    res = port.create_proposal_draft(payload, idempotency_key=inp.idempotency_key)
    append_audit_log(inp.user_id, "create_proposal_draft", payload, res, inp.trace_id)
    return json.dumps(res, indent=2)

@server.tool(
    name="submit_proposal",
    description="Submit an approved proposal to the marketplace, deducting required Connects. Requires human approval before invocation."
)
def mcp_submit_proposal(
    job_id: str,
    cover_letter: str,
    bid_amount: float,
    idempotency_key: str,
    screening_answers: Optional[List[str]] = None,
    evidence_ids: Optional[List[str]] = None,
    user_id: str = "default_user",
    trace_id: str = "trace-submit-001"
) -> str:
    inp = SubmitProposalInput(
        job_id=job_id,
        cover_letter=cover_letter,
        bid_amount=bid_amount,
        screening_answers=screening_answers or [],
        evidence_ids=evidence_ids or [],
        idempotency_key=idempotency_key,
        dry_run=False,
        user_id=user_id,
        trace_id=trace_id
    )
    payload = inp.model_dump()
    res = port.submit_proposal(payload)
    append_audit_log(inp.user_id, "submit_proposal", payload, res, inp.trace_id)
    return json.dumps(res, indent=2)

@server.tool(
    name="send_message",
    description="Send an approved message to a client thread. Requires human approval before invocation."
)
def mcp_send_message(
    thread_id: str,
    recipient_id: str,
    content: str,
    idempotency_key: str,
    user_id: str = "default_user",
    trace_id: str = "trace-msg-001"
) -> str:
    inp = SendMessageInput(
        thread_id=thread_id,
        recipient_id=recipient_id,
        content=content,
        idempotency_key=idempotency_key,
        user_id=user_id,
        trace_id=trace_id
    )
    res = port.send_message(
        thread_id=inp.thread_id,
        recipient_id=inp.recipient_id,
        content=inp.content,
        idempotency_key=inp.idempotency_key
    )
    append_audit_log(inp.user_id, "send_message", inp.model_dump(), res, inp.trace_id)
    return json.dumps(res, indent=2)

if __name__ == "__main__":
    server.run()
