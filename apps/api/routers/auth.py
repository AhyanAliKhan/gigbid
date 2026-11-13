"""
Auth & Onboarding Router
"""

from fastapi import APIRouter, HTTPException
from apps.api.auth.token_store import auth_store
from apps.api.schemas.api_models import LoginRequest, PersonaSwitchRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])

PERSONAS_INFO = {
    "alex_chen_aiml": {
        "id": "alex_chen_aiml",
        "name": "Alex Chen",
        "domain": "AI/ML",
        "headline": "Senior AI & Machine Learning Engineer",
        "hourly_rate": 85.0,
        "verified_case_studies": 20,
        "skills": ["Python", "PyTorch", "vLLM", "LangGraph", "FastAPI", "Vector Databases"]
    },
    "sarah_jenkins_fullstack": {
        "id": "sarah_jenkins_fullstack",
        "name": "Sarah Jenkins",
        "domain": "Full-Stack Web",
        "headline": "Principal Full-Stack Web & Cloud Architect",
        "hourly_rate": 75.0,
        "verified_case_studies": 20,
        "skills": ["TypeScript", "React", "Next.js", "FastAPI", "PostgreSQL", "Docker"]
    },
    "marcus_vance_analyst": {
        "id": "marcus_vance_analyst",
        "name": "Marcus Vance",
        "domain": "Data Analytics",
        "headline": "Lead Data Analyst & Business Intelligence Specialist",
        "hourly_rate": 65.0,
        "verified_case_studies": 20,
        "skills": ["SQL", "Snowflake", "dbt", "PowerBI", "Python", "Tableau"]
    }
}

@router.post("/login")
def login(req: LoginRequest):
    session = auth_store.authenticate_reviewer(req.username, req.pin)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid reviewer credentials")
    return {"status": "authenticated", "session": session}

@router.get("/me")
def get_current_user():
    session = auth_store.get_session()
    pid = session.get("active_persona", "alex_chen_aiml")
    return {
        "user": session,
        "persona_details": PERSONAS_INFO.get(pid, PERSONAS_INFO["alex_chen_aiml"]),
        "available_personas": list(PERSONAS_INFO.values())
    }

@router.post("/persona")
def switch_persona(req: PersonaSwitchRequest):
    if req.persona_id not in PERSONAS_INFO:
        raise HTTPException(status_code=400, detail="Invalid persona ID")
    auth_store.set_active_persona("reviewer_01", req.persona_id)
    return {"status": "ok", "active_persona": req.persona_id, "details": PERSONAS_INFO[req.persona_id]}
