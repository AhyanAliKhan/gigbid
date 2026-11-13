"""
Unit tests for FastAPI routers and health check endpoints.
"""

import pytest
from apps.api.main import app
from apps.api.routers.auth import login, get_current_user, switch_persona
from apps.api.routers.jobs import get_job_inbox, get_job_detail
from apps.api.routers.settings import get_settings
from apps.api.schemas.api_models import LoginRequest, PersonaSwitchRequest

def test_api_health_check():
    from apps.api.main import health
    res = health()
    assert res["status"] == "ok"
    assert res["service"] == "gigbid-api"
    assert "degraded_mode" in res

def test_auth_endpoints():
    login_res = login(LoginRequest(username="reviewer", pin="gigbid2026"))
    assert login_res["status"] == "authenticated"
    
    user_info = get_current_user()
    assert "user" in user_info
    assert "available_personas" in user_info

    switch_res = switch_persona(PersonaSwitchRequest(persona_id="sarah_jenkins_fullstack"))
    assert switch_res["active_persona"] == "sarah_jenkins_fullstack"

def test_jobs_inbox_and_detail():
    inbox = get_job_inbox(category="AI/ML", limit=5)
    assert inbox["total"] >= 0
    assert "jobs" in inbox

    job_detail = get_job_detail("job-0001")
    assert "job" in job_detail
    assert "requirement_evidence_matrix" in job_detail

def test_settings_and_memory():
    settings = get_settings()
    assert "settings" in settings
    assert "style_memory_rules" in settings
    assert len(settings["style_memory_rules"]) >= 1
