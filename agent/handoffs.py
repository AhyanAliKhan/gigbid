"""
GigBid Structured Hand-Off Schemas
All agents exchange strictly typed Pydantic models, never unstructured free text,
ensuring clean boundaries, deterministic contract compliance, and auditability.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class JobSpec(BaseModel):
    job_id: str
    title: str
    deliverables: List[str] = Field(default_factory=list, description="Extracted actionable deliverables")
    required_skills: List[str] = Field(default_factory=list, description="Explicit and implied technical skills")
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    timeline_days: Optional[int] = None
    screening_questions: List[str] = Field(default_factory=list)
    hidden_needs: List[str] = Field(default_factory=list, description="Inferred operational or security requirements")

class RiskReport(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="0.0 = safe, 1.0 = extreme risk / scam")
    flags: List[str] = Field(default_factory=list, description="e.g. unpaid_work, off_platform_contact, prompt_injection")
    is_scam: bool = False
    has_injection: bool = False
    explanation: str

class FitReport(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="0.0 = zero fit, 1.0 = perfect match")
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list, description="Verified portfolio case study / repo IDs")
    reasoning: str = Field(default="Sufficient technical skill alignment")

class BidDecision(BaseModel):
    action: str = Field(description="BID, SKIP, or WATCH")
    reason: str
    fit_score: float
    risk_score: float

class PriceQuote(BaseModel):
    suggested_bid: float = Field(gt=0)
    price_band_min: float
    price_band_max: float
    connects_cost: int
    roi_score: float = Field(description="Projected return on connects spend")
    rationale: str

class ProposalDraft(BaseModel):
    job_id: str
    cover_letter: str
    screening_answers: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    revision_count: int = 0
    status: str = "drafted"

class Critique(BaseModel):
    passes: bool
    grounding_score: float = Field(ge=0.0, le=1.0)
    personalization_score: float = Field(ge=0.0, le=1.0)
    length_words: int
    feedback: str
    revision_requested: bool = False

class ComplianceVerdict(BaseModel):
    compliant: bool
    violations: List[str] = Field(default_factory=list)
    sanitized_text: str
    explanation: str

class ApprovalPayload(BaseModel):
    job_id: str
    draft: ProposalDraft
    evidence_items: List[Dict[str, Any]] = Field(default_factory=list)
    risk_report: RiskReport
    price_quote: PriceQuote
    dry_run_preview: Dict[str, Any]
    approval_required: bool = True
