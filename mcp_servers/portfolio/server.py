"""
Portfolio MCP Server
Exposes verified portfolio evidence tools, resource templates, and prompt templates.
Built with the official MCP Python SDK (MCPServer).
"""

import sys
from typing import List, Dict, Any, Optional
from mcp.server.mcpserver import MCPServer
from mcp_servers.portfolio.tools import search_evidence, get_case_study, list_skills
from mcp_servers.portfolio.resources import read_case_resource, read_proposal_resource
from mcp_servers.portfolio.prompts import prompt_answer_screening_question, prompt_summarize_proof_points

server = MCPServer("portfolio-mcp-server")

# -------------------------------------------------------------
# MCP Tools
# -------------------------------------------------------------
@server.tool(
    name="search_evidence",
    description="Search verified portfolio evidence matching a client requirement. Returns evidence items with type, source, date, and outcome."
)
def mcp_search_evidence(requirement: str, k: int = 5, filters: Optional[Dict[str, Any]] = None) -> str:
    results = search_evidence(requirement, k=k, filters=filters)
    import json
    return json.dumps(results, indent=2)

@server.tool(
    name="get_case_study",
    description="Retrieve full details and architecture markdown for a specific case study by ID."
)
def mcp_get_case_study(id: str) -> str:
    result = get_case_study(id)
    import json
    return json.dumps(result, indent=2)

@server.tool(
    name="list_skills",
    description="List all verified technical skills claimed in the active freelancer portfolio."
)
def mcp_list_skills() -> str:
    skills = list_skills()
    import json
    return json.dumps(skills, indent=2)

# -------------------------------------------------------------
# MCP Resources
# -------------------------------------------------------------
@server.resource("portfolio://case/{id}")
def case_resource(id: str) -> str:
    """Load full case study item by ID."""
    return read_case_resource(id)

@server.resource("portfolio://proposal/{id}")
def proposal_resource(id: str) -> str:
    """Load full past proposal item with outcome."""
    return read_proposal_resource(id)

# -------------------------------------------------------------
# MCP Prompts
# -------------------------------------------------------------
@server.prompt("answer_screening_question")
def prompt_screening(question: str, skill_context: str = "") -> str:
    return prompt_answer_screening_question(question, skill_context)

@server.prompt("summarize_proof_points")
def prompt_proof(requirement: str, evidence_text: str = "") -> str:
    return prompt_summarize_proof_points(requirement, evidence_text)

if __name__ == "__main__":
    # Runs over stdio transport by default
    server.run()
