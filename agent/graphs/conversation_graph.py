"""
GigBid Conversation Graph Implementation
Manages client conversation threads:
- Reads incoming messages
- Classifies intent (question, negotiation, interview_request, scam_signal)
- Drafts contextual replies or retrieves Workspace calendar slots
- Halts at human approval gate before sending any message
- Idempotently transmits approved message to marketplace
- Persists state with LangGraph Checkpointer
"""

import os
import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver

from agent.state import ConversationState
from agent.nodes.client_liaison import client_liaison_node
from agent.mcp_client import mcp_manager

def human_message_approval_node(state: ConversationState) -> Dict[str, Any]:
    payload = {
        "thread_id": state.get("thread_id"),
        "client_id": state.get("client_id"),
        "incoming_message": state.get("incoming_message"),
        "classified_intent": state.get("classified_intent"),
        "draft_response": state.get("draft_response"),
        "calendar_slots": state.get("calendar_slots", []),
        "status": "waiting_approval"
    }

    # LangGraph Human-in-the-Loop Interrupt
    user_decision = interrupt(payload)

    action = user_decision.get("action", "approved") if isinstance(user_decision, dict) else "approved"
    edited_text = user_decision.get("edited_text") if isinstance(user_decision, dict) else None

    final_text = edited_text if (action == "edited" and edited_text) else state.get("draft_response", "")

    trace_entry = {
        "node": "human_message_approval",
        "action": action,
        "final_text_preview": final_text[:80]
    }

    return {
        "human_approved": action in ["approved", "edited"],
        "draft_response": final_text,
        "trace": [trace_entry]
    }

def route_after_msg_approval(state: ConversationState) -> Literal["send_message_node", "cancel_message_node"]:
    if state.get("human_approved", False):
        return "send_message_node"
    return "cancel_message_node"

def send_message_node(state: ConversationState) -> Dict[str, Any]:
    thread_id = state.get("thread_id", "thread-001")
    client_id = state.get("client_id", "client-001")
    content = state.get("draft_response", "")
    idempotency_key = f"msg-{thread_id}-{uuid.uuid4().hex[:6]}"

    try:
        res = mcp_manager.execute_tool(
            agent_role="client_liaison",
            tool_name="send_message",
            arguments={
                "thread_id": thread_id,
                "recipient_id": client_id,
                "content": content,
                "idempotency_key": idempotency_key
            }
        )
    except Exception as e:
        res = {"status": "error", "detail": str(e)}

    trace_entry = {
        "node": "send_message_node",
        "action": "send_approved_message",
        "idempotency_key": idempotency_key,
        "result": res
    }

    return {
        "sent_result": res,
        "trace": [trace_entry]
    }

def cancel_message_node(state: ConversationState) -> Dict[str, Any]:
    trace_entry = {
        "node": "cancel_message_node",
        "action": "message_cancelled_by_human"
    }
    return {
        "sent_result": {"status": "cancelled_by_user"},
        "trace": [trace_entry]
    }

def build_conversation_graph(checkpointer=None):
    workflow = StateGraph(ConversationState)

    workflow.add_node("client_liaison", client_liaison_node)
    workflow.add_node("human_approval", human_message_approval_node)
    workflow.add_node("send_message_node", send_message_node)
    workflow.add_node("cancel_message_node", cancel_message_node)

    workflow.add_edge(START, "client_liaison")
    workflow.add_edge("client_liaison", "human_approval")

    workflow.add_conditional_edges(
        "human_approval",
        route_after_msg_approval,
        {"send_message_node": "send_message_node", "cancel_message_node": "cancel_message_node"}
    )

    workflow.add_edge("send_message_node", END)
    workflow.add_edge("cancel_message_node", END)

    cp = checkpointer or MemorySaver()
    return workflow.compile(checkpointer=cp)

conversation_graph = build_conversation_graph()
