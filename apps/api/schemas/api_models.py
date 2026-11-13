"""
FastAPI Request & Response Schemas
Provides strictly typed contracts for OpenAPI generation and frontend consumption.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    pin: str

class PersonaSwitchRequest(BaseModel):
    persona_id: str

class RunJobRequest(BaseModel):
    job_id: str
    persona_id: Optional[str] = None

class ApprovalDecisionRequest(BaseModel):
    thread_id: str
    action: str = Field(description="'approved', 'edited', or 'rejected'")
    feedback: Optional[str] = None
    edited_text: Optional[str] = None

class RegenerateParagraphRequest(BaseModel):
    original_text: str
    instruction: str
    paragraph_index: int = 0

class SettingsUpdateRequest(BaseModel):
    autonomy_level: str = Field(default="semi_autonomous", description="manual, semi_autonomous, conservative")
    auto_skip_threshold: float = Field(default=0.40, ge=0.0, le=1.0)
    weekly_connects_budget: int = Field(default=120, ge=10)
    rate_floor_usd: float = Field(default=35.0, ge=10.0)

class DeleteMemoryRuleRequest(BaseModel):
    rule_id: str

class SendMessageRequest(BaseModel):
    thread_id: str
    client_id: str
    content: str
    approved: bool = True
