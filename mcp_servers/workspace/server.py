"""
Workspace MCP Server
Provides tools for checking calendar availability, creating tentative interview holds,
and preparing client email drafts.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from mcp.server.mcpserver import MCPServer

server = MCPServer("workspace-mcp-server")

# In-memory holds and drafts store
CALENDAR_HOLDS: List[Dict[str, Any]] = []
EMAIL_DRAFTS: List[Dict[str, Any]] = []

class CalendarSlotsInput(BaseModel):
    start_date: Optional[str] = Field(default=None, description="ISO format start date YYYY-MM-DD")
    days_ahead: int = Field(default=5, ge=1, le=14)

class InterviewHoldInput(BaseModel):
    title: str = Field(min_length=3)
    start_time: str = Field(description="ISO format timestamp")
    duration_minutes: int = Field(default=30, ge=15, le=120)
    attendee_email: Optional[str] = None
    notes: Optional[str] = None

class EmailDraftInput(BaseModel):
    recipient_email: str = Field(min_length=5)
    subject: str = Field(min_length=3)
    body: str = Field(min_length=10)

@server.tool(
    name="get_free_calendar_slots",
    description="Retrieve available 30-minute interview time slots across business hours (9:00 - 17:00 UTC)."
)
def mcp_get_free_calendar_slots(start_date: Optional[str] = None, days_ahead: int = 5) -> str:
    base = datetime.utcnow()
    slots = []
    for day in range(1, days_ahead + 1):
        target_day = base + timedelta(days=day)
        # Skip weekends
        if target_day.weekday() >= 5:
            continue
        date_str = target_day.strftime("%Y-%m-%d")
        for hour in [14, 15, 16, 17, 18]: # UTC afternoon / US morning
            slot_iso = f"{date_str}T{hour:02d}:00:00Z"
            # Check not already held
            if not any(h["start_time"] == slot_iso for h in CALENDAR_HOLDS):
                slots.append({
                    "slot_time": slot_iso,
                    "duration_minutes": 30,
                    "timezone": "UTC",
                    "formatted": f"{date_str} at {hour:02d}:00 UTC"
                })
    return json.dumps({"available_slots": slots[:8]}, indent=2)

@server.tool(
    name="create_tentative_interview_hold",
    description="Reserve a tentative calendar hold for an upcoming client interview."
)
def mcp_create_tentative_interview_hold(
    title: str,
    start_time: str,
    duration_minutes: int = 30,
    attendee_email: Optional[str] = None,
    notes: Optional[str] = None
) -> str:
    hold = {
        "hold_id": f"hold-{len(CALENDAR_HOLDS)+1:03d}",
        "title": title,
        "start_time": start_time,
        "duration_minutes": duration_minutes,
        "attendee_email": attendee_email,
        "notes": notes,
        "status": "tentative_hold",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    CALENDAR_HOLDS.append(hold)
    return json.dumps({"status": "success", "hold": hold}, indent=2)

@server.tool(
    name="create_email_draft",
    description="Create a draft email in the user's workspace mailbox for client follow-up."
)
def mcp_create_email_draft(recipient_email: str, subject: str, body: str) -> str:
    draft = {
        "draft_id": f"draft-{len(EMAIL_DRAFTS)+1:03d}",
        "recipient_email": recipient_email,
        "subject": subject,
        "body": body,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    EMAIL_DRAFTS.append(draft)
    return json.dumps({"status": "success", "draft": draft}, indent=2)

if __name__ == "__main__":
    server.run()
