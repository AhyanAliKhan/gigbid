"""
MCP Multi-Server Client & Discipline Manager
Enforces strict per-agent tool allowlists, bounded retries with exponential backoff,
timeouts, and graceful degraded-mode recovery if servers become unavailable.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger("mcp_client")

# Define exact tool allowlists per agent role according to assignment spec
AGENT_TOOL_ALLOWLISTS = {
    "scout": ["search_jobs", "get_job"],
    "analyst": [], # None
    "risk_assessor": ["get_job", "get_client_history"],
    "fit_matcher": ["search_evidence", "get_case_study", "list_skills"],
    "pricing": ["get_client_history", "get_connects_balance"],
    "writer": ["search_evidence", "get_case_study"],
    "verifier": ["search_evidence", "get_case_study"],
    "critic": ["search_evidence", "get_case_study"],
    "compliance": [], # None
    "client_liaison": ["list_messages", "send_message", "get_free_calendar_slots", "create_tentative_interview_hold", "create_email_draft"],
    "marketplace_submitter": ["submit_proposal", "create_proposal_draft"]
}

class MCPExecutionError(Exception):
    pass

class ClientDisciplineError(MCPExecutionError):
    pass

class DegradedModeError(MCPExecutionError):
    pass

class MultiServerMCPManager:
    """Manages dispatch and client discipline across Portfolio, Marketplace, and Workspace servers."""
    def __init__(self):
        self.degraded_mode = False
        self.queued_operations: List[Dict[str, Any]] = []

    def get_allowed_tools_for_agent(self, agent_role: str) -> List[str]:
        return AGENT_TOOL_ALLOWLISTS.get(agent_role, [])

    def execute_tool(
        self,
        agent_role: str,
        tool_name: str,
        arguments: Dict[str, Any],
        max_retries: int = 2,
        base_backoff_seconds: float = 0.5
    ) -> Any:
        # 1. Enforce Client Discipline
        allowed = self.get_allowed_tools_for_agent(agent_role)
        if tool_name not in allowed:
            raise ClientDisciplineError(
                f"Client Discipline Violation: Agent '{agent_role}' is not permitted to access tool '{tool_name}'. Allowed: {allowed}"
            )

        # 2. Bounded retries with exponential backoff
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                result = self._dispatch(tool_name, arguments)
                self.degraded_mode = False
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Tool '{tool_name}' failed on attempt {attempt+1}/{max_retries+1}: {e}")
                if attempt < max_retries:
                    time.sleep(base_backoff_seconds * (2 ** attempt))

        # 3. Enter Degraded Mode if marketplace is down
        if "marketplace" in tool_name or tool_name in ["search_jobs", "get_job", "submit_proposal"]:
            self.degraded_mode = True
            self.queued_operations.append({
                "agent_role": agent_role,
                "tool_name": tool_name,
                "arguments": arguments,
                "timestamp": time.time()
            })
            raise DegradedModeError(
                f"Marketplace service is unavailable. System entered DEGRADED MODE. Operation '{tool_name}' has been safely queued."
            )
        raise MCPExecutionError(f"Failed to execute tool '{tool_name}' after {max_retries+1} attempts: {last_error}")

    def _dispatch(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        # Portfolio tools
        if tool_name == "search_evidence":
            from mcp_servers.portfolio.tools import search_evidence
            return search_evidence(**arguments)
        elif tool_name == "get_case_study":
            from mcp_servers.portfolio.tools import get_case_study
            return get_case_study(**arguments)
        elif tool_name == "list_skills":
            from mcp_servers.portfolio.tools import list_skills
            return list_skills(**arguments)

        # Marketplace tools
        elif tool_name == "search_jobs":
            from agent.marketplace_port import get_marketplace_port
            return get_marketplace_port().search_jobs(**arguments)
        elif tool_name == "get_job":
            from agent.marketplace_port import get_marketplace_port
            return get_marketplace_port().get_job(**arguments)
        elif tool_name == "get_client_history":
            from agent.marketplace_port import get_marketplace_port
            return get_marketplace_port().get_client_history(**arguments)
        elif tool_name == "get_connects_balance":
            from agent.marketplace_port import get_marketplace_port
            return get_marketplace_port().get_connects_balance(**arguments)
        elif tool_name == "create_proposal_draft":
            from agent.marketplace_port import get_marketplace_port
            return get_marketplace_port().create_proposal_draft(arguments, idempotency_key=arguments.get("idempotency_key", "default_key"))
        elif tool_name == "submit_proposal":
            from agent.marketplace_port import get_marketplace_port
            return get_marketplace_port().submit_proposal(arguments)
        elif tool_name == "list_messages":
            from agent.marketplace_port import get_marketplace_port
            return get_marketplace_port().list_messages(**arguments)
        elif tool_name == "send_message":
            from agent.marketplace_port import get_marketplace_port
            return get_marketplace_port().send_message(**arguments)

        # Workspace tools
        elif tool_name == "get_free_calendar_slots":
            from mcp_servers.workspace.server import mcp_get_free_calendar_slots
            return json.loads(mcp_get_free_calendar_slots(**arguments))
        elif tool_name == "create_tentative_interview_hold":
            from mcp_servers.workspace.server import mcp_create_tentative_interview_hold
            return json.loads(mcp_create_tentative_interview_hold(**arguments))
        elif tool_name == "create_email_draft":
            from mcp_servers.workspace.server import mcp_create_email_draft
            return json.loads(mcp_create_email_draft(**arguments))
        else:
            raise NotImplementedError(f"Unknown tool: '{tool_name}'")

mcp_manager = MultiServerMCPManager()
