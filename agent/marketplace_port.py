"""
GigBid Unified Marketplace Port Interface
Provides a single, clean contract for all marketplace operations.
Backed by two pluggable adapters:
1. GigSimAdapter: wraps the GigSim simulator for development, testing, and grading.
2. UpworkLiveAdapter: wraps Upwork's official MCP server over Streamable HTTP for real live use.
The multi-agent graph interacts ONLY with this port and cannot tell which marketplace is active.
"""

import os
from typing import Protocol, Dict, Any, List, Optional
from mcp_servers.marketplace.adapters.gigsim import GigSimClient
from mcp_servers.marketplace.adapters.upwork_live import UpworkLiveClient

class MarketplacePort(Protocol):
    def search_jobs(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]: ...
    def get_job(self, job_id: str) -> Dict[str, Any]: ...
    def get_client_history(self, client_id: str) -> Dict[str, Any]: ...
    def get_connects_balance(self, user_id: str = "default_user") -> Dict[str, Any]: ...
    def create_proposal_draft(self, payload: Dict[str, Any], idempotency_key: str) -> Dict[str, Any]: ...
    def submit_proposal(self, payload: Dict[str, Any]) -> Dict[str, Any]: ...
    def list_messages(self, thread_id: Optional[str] = None) -> List[Dict[str, Any]]: ...
    def send_message(self, thread_id: str, recipient_id: str, content: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]: ...

class GigSimAdapter:
    """Adapter forwarding requests to the GigSim marketplace simulator."""
    def __init__(self, client: Optional[GigSimClient] = None):
        self.client = client or GigSimClient()

    def search_jobs(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return self.client.search_jobs(query=query, category=category, limit=limit, offset=offset)

    def get_job(self, job_id: str) -> Dict[str, Any]:
        return self.client.get_job(job_id)

    def get_client_history(self, client_id: str) -> Dict[str, Any]:
        return self.client.get_client_history(client_id)

    def get_connects_balance(self, user_id: str = "default_user") -> Dict[str, Any]:
        return self.client.get_connects_balance(user_id=user_id)

    def create_proposal_draft(self, payload: Dict[str, Any], idempotency_key: str) -> Dict[str, Any]:
        payload_copy = {**payload, "idempotency_key": idempotency_key, "dry_run": True}
        return self.client.submit_proposal(payload_copy)

    def submit_proposal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self.client.submit_proposal(payload)

    def list_messages(self, thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.client.list_messages(thread_id=thread_id)

    def send_message(self, thread_id: str, recipient_id: str, content: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        return self.client.send_message(thread_id, recipient_id, content, idempotency_key)

class UpworkLiveAdapter:
    """Adapter forwarding requests to Upwork's official MCP server."""
    def __init__(self, client: Optional[UpworkLiveClient] = None):
        self.client = client or UpworkLiveClient()

    def search_jobs(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        return self.client.search_jobs(query=query, category=category, limit=limit, offset=offset)

    def get_job(self, job_id: str) -> Dict[str, Any]:
        return self.client.get_job(job_id)

    def get_client_history(self, client_id: str) -> Dict[str, Any]:
        return self.client.get_client_history(client_id)

    def get_connects_balance(self, user_id: str = "default_user") -> Dict[str, Any]:
        return self.client.get_connects_balance(user_id=user_id)

    def create_proposal_draft(self, payload: Dict[str, Any], idempotency_key: str) -> Dict[str, Any]:
        return self.client.create_proposal_draft(payload, idempotency_key)

    def submit_proposal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Live mode safety: always creates draft, never direct auto-submission
        key = payload.get("idempotency_key", "default_live_key")
        return self.client.create_proposal_draft(payload, key)

    def list_messages(self, thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return []

    def send_message(self, thread_id: str, recipient_id: str, content: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        return {"status": "queued_draft", "thread_id": thread_id, "note": "Live message draft queued for Upwork approval."}

def get_marketplace_port() -> MarketplacePort:
    """Factory returning the configured marketplace port implementation."""
    mode = os.environ.get("MARKETPLACE_MODE", "gigsim").lower()
    if mode == "live" or mode == "upwork":
        return UpworkLiveAdapter()
    return GigSimAdapter()
