"""
Unit tests for Portfolio, Marketplace, and Workspace MCP Servers.
"""

import pytest
import json
from mcp_servers.portfolio.tools import search_evidence, get_case_study, list_skills
from mcp_servers.portfolio.resources import read_case_resource, read_proposal_resource
from mcp_servers.workspace.server import mcp_get_free_calendar_slots, mcp_create_tentative_interview_hold
from agent.mcp_client import mcp_manager, ClientDisciplineError, DegradedModeError

def test_portfolio_search_evidence():
    results = search_evidence("RAG hybrid search", k=3, persona_id="alex_chen_aiml")
    assert len(results) > 0
    assert "evidence_id" in results[0]
    assert "title" in results[0]
    assert "relevance_score" in results[0]
    assert results[0]["type"] in ["case_study", "repository"]

def test_portfolio_get_case_study():
    cs = get_case_study("CS-ALEX-001", persona_id="alex_chen_aiml")
    assert "id" in cs
    assert cs["id"] == "CS-ALEX-001"
    assert "skills" in cs

def test_portfolio_list_skills():
    skills = list_skills("alex_chen_aiml")
    assert len(skills) > 0
    assert isinstance(skills, list)
    assert any("Python" in s for s in skills)

def test_portfolio_resources():
    case_res = read_case_resource("CS-ALEX-001")
    assert len(case_res) > 20
    prop_res = read_proposal_resource("PROP-ALEX-001")
    assert len(prop_res) > 20

def test_workspace_calendar_slots():
    slots_json = mcp_get_free_calendar_slots(days_ahead=3)
    slots = json.loads(slots_json)
    assert "available_slots" in slots
    assert len(slots["available_slots"]) > 0
    assert "slot_time" in slots["available_slots"][0]

def test_workspace_interview_hold():
    res_json = mcp_create_tentative_interview_hold(
        title="Screening Call",
        start_time="2026-11-20T16:00:00Z"
    )
    res = json.loads(res_json)
    assert res["status"] == "success"
    assert res["hold"]["title"] == "Screening Call"

def test_mcp_client_discipline_enforcement():
    # Job Analyst has empty tool allowlist: attempting to call search_jobs must raise ClientDisciplineError
    with pytest.raises(ClientDisciplineError):
        mcp_manager.execute_tool(
            agent_role="analyst",
            tool_name="search_jobs",
            arguments={"query": "python"}
        )

def test_mcp_client_allowed_tool_dispatch():
    # Scout is permitted to call search_jobs
    res = mcp_manager.execute_tool(
        agent_role="scout",
        tool_name="search_jobs",
        arguments={"limit": 2}
    )
    assert "jobs" in res
    assert len(res["jobs"]) <= 2
