"""
Client Liaison Agent Node (Conversation Graph)
Processes incoming client messages, classifies intent, drafts contextual responses,
queries Workspace MCP for available interview calendar slots, and prepares for human approval.
Tool Access: Marketplace (read, write after approval), Workspace.
"""

import os
from typing import Dict, Any
from agent.state import ConversationState
from agent.mcp_client import mcp_manager

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "client_liaison_v1.md")

def client_liaison_node(state: ConversationState) -> Dict[str, Any]:
    msg = state.get("incoming_message", {})
    content = msg.get("content", "").lower()
    thread_id = state.get("thread_id", "thread-001")
    
    # 1. Classify Intent
    if any(kw in content for kw in ["interview", "call", "schedule", "talk", "chat tomorrow", "zoom", "meet"]):
        intent = "interview_request"
        confidence = 0.94
    elif any(kw in content for kw in ["rate", "budget", "discount", "lower", "price", "cheaper"]):
        intent = "negotiation"
        confidence = 0.88
    elif any(kw in content for kw in ["telegram", "whatsapp", "crypto", "free test", "off platform"]):
        intent = "scam_signal"
        confidence = 0.98
    else:
        intent = "question"
        confidence = 0.85

    # 2. Query Workspace MCP for calendar slots if interview request
    calendar_slots = []
    draft_response = ""
    if intent == "interview_request":
        try:
            slots_res = mcp_manager.execute_tool("client_liaison", "get_free_calendar_slots", {"days_ahead": 3})
            calendar_slots = slots_res.get("available_slots", []) if isinstance(slots_res, dict) else []
        except Exception:
            pass

        slot_strs = [s.get("formatted", s.get("slot_time")) for s in calendar_slots[:2]]
        slots_formatted = " or ".join(slot_strs) if slot_strs else "tomorrow at 15:00 UTC"

        draft_response = (
            f"Hi! Thank you for the update. I would be glad to speak with your team. "
            f"I have availability for a 30-minute introductory call on {slots_formatted}. "
            f"Please let me know if either of those times suits your schedule, or feel free to suggest an alternative!"
        )
    elif intent == "scam_signal":
        draft_response = (
            "Thank you for reaching out. Per marketplace terms of service, all project communications and milestones "
            "must remain strictly within the platform. I look forward to working with you here."
        )
    elif intent == "negotiation":
        draft_response = (
            "Thank you for discussing the project scope. The proposed price reflects complete production delivery, "
            "comprehensive test coverage, and milestone support. I can explore staging milestones to align with your monthly budget."
        )
    else: # question
        draft_response = (
            "Hi! Thanks for the question. Yes, my implementation approach includes comprehensive unit and integration testing, "
            "clean documentation, and full containerization to guarantee seamless hand-off."
        )

    trace_entry = {
        "node": "client_liaison",
        "action": "process_message",
        "intent": intent,
        "confidence": confidence,
        "calendar_slots_retrieved": len(calendar_slots),
        "tokens": 290
    }

    return {
        "classified_intent": intent,
        "intent_confidence": confidence,
        "calendar_slots": calendar_slots,
        "draft_response": draft_response,
        "human_approved": False,
        "trace": [trace_entry]
    }
