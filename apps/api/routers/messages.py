"""
Messages & Client Liaison Router
Manages conversation threads, suggested replies, calendar interview slots,
and human approval gate before sending messages.
"""

from typing import Optional
from fastapi import APIRouter
from gigsim.server import list_messages, send_message, MessagePayload
from mcp_servers.workspace.server import mcp_get_free_calendar_slots
from apps.api.schemas.api_models import SendMessageRequest
import json

router = APIRouter(prefix="/api/messages", tags=["messages"])

@router.get("/threads")
def get_threads():
    all_msgs = list_messages()
    threads_map = {}
    for m in all_msgs:
        tid = m.get("thread_id", "thread-default")
        threads_map.setdefault(tid, []).append(m)

    summary = []
    for tid, msgs in threads_map.items():
        last = msgs[-1]
        summary.append({
            "thread_id": tid,
            "job_id": last.get("job_id", "job-unknown"),
            "sender_id": last.get("sender_id", "client"),
            "last_message": last.get("content", ""),
            "timestamp": last.get("timestamp", ""),
            "requires_reply": last.get("requires_reply", False),
            "message_count": len(msgs)
        })

    # Add default mock conversation if empty
    if not summary:
        summary.append({
            "thread_id": "thread-job-0042",
            "job_id": "job-0042",
            "sender_id": "EnterpriseClient_09",
            "last_message": "Hi! We reviewed your proposal and were impressed by your case study benchmarks. Are you available for a 20-minute introductory call tomorrow?",
            "timestamp": "2026-11-13T14:15:00Z",
            "requires_reply": True,
            "message_count": 1
        })
    return summary

@router.get("/{thread_id}")
def get_thread_detail(thread_id: str):
    msgs = list_messages(thread_id=thread_id)
    if not msgs:
        # Default mock detail
        msgs = [
            {
                "message_id": "msg-001",
                "thread_id": thread_id,
                "sender_id": "EnterpriseClient_09",
                "sender_role": "client",
                "content": "Hi! We reviewed your proposal and were impressed by your case study benchmarks. Are you available for a 20-minute introductory call tomorrow?",
                "timestamp": "2026-11-13T14:15:00Z"
            }
        ]
    
    # Retrieve available calendar slots from Workspace MCP
    slots_json = mcp_get_free_calendar_slots(days_ahead=3)
    slots = json.loads(slots_json).get("available_slots", [])

    slot_strs = [s.get("formatted", s.get("slot_time")) for s in slots[:2]]
    suggested = (
        f"Hi! Thank you for considering my proposal. I would be glad to meet with your team. "
        f"I have availability for a brief call tomorrow at {slot_strs[0] if slot_strs else '15:00 UTC'} "
        f"or {slot_strs[1] if len(slot_strs)>1 else '17:00 UTC'}. Looking forward to connecting!"
    )

    return {
        "thread_id": thread_id,
        "messages": msgs,
        "suggested_reply": suggested,
        "calendar_slots": slots,
        "intent_detected": "interview_request"
    }

@router.post("/send")
def post_send_message(req: SendMessageRequest):
    res = send_message(MessagePayload(
        thread_id=req.thread_id,
        recipient_id=req.client_id,
        content=req.content,
        idempotency_key=f"send-{req.thread_id}"
    ))
    return {"status": "sent", "result": res}
