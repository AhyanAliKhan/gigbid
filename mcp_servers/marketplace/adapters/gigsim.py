"""
GigSim Adapter
Interacts with the GigSim Marketplace Simulator REST API.
"""

import os
import httpx
from typing import Dict, Any, List, Optional

class GigSimClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = (base_url or os.environ.get("GIGSIM_BASE_URL", "http://localhost:8081")).rstrip("/")
        self.token = token or os.environ.get("GIGSIM_API_TOKEN", "gigsim_dev_token")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _sync_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {**self.headers, **kwargs.pop("headers", {})}
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.request(method, url, headers=headers, **kwargs)
                if resp.status_code == 429:
                    raise RuntimeError("GigSim Rate Limit Exceeded (429). Retry-After: " + resp.headers.get("Retry-After", "5"))
                if resp.status_code >= 500:
                    raise RuntimeError(f"GigSim Server Error ({resp.status_code}): {resp.text}")
                resp.raise_for_status()
                return resp.json()
        except httpx.ConnectError:
            # Degraded mode fallback: direct in-memory call if local
            from gigsim.server import search_jobs as local_search, get_job as local_get_job, get_client_history as local_client, get_connects_balance as local_bal, submit_proposal as local_submit, list_messages as local_msgs, send_message as local_send, ProposalSubmission, MessagePayload
            if path == "/health":
                return {"status": "ok", "service": "gigsim", "version": "1.0.0"}
            if path.startswith("/jobs/"):
                jid = path.split("/")[-1]
                return local_get_job(jid)
            if path.startswith("/jobs"):
                params = kwargs.get("params", {})
                return local_search(**params)
            if path.startswith("/clients/"):
                cid = path.split("/")[-1]
                return local_client(cid)
            if path.startswith("/connects/balance"):
                return local_bal()
            if path == "/proposals":
                body = kwargs.get("json", {})
                return local_submit(ProposalSubmission(**body))
            if path == "/messages":
                if method.upper() == "GET":
                    return local_msgs()
                body = kwargs.get("json", {})
                return local_send(MessagePayload(**body))
            raise

    def search_jobs(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        params = {"limit": limit, "offset": offset}
        if query:
            params["query"] = query
        if category:
            params["category"] = category
        return self._sync_request("GET", "/jobs", params=params)

    def get_job(self, job_id: str) -> Dict[str, Any]:
        return self._sync_request("GET", f"/jobs/{job_id}")

    def get_client_history(self, client_id: str) -> Dict[str, Any]:
        return self._sync_request("GET", f"/clients/{client_id}")

    def get_connects_balance(self, user_id: str = "default_user") -> Dict[str, Any]:
        return self._sync_request("GET", "/connects/balance", params={"user_id": user_id})

    def submit_proposal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._sync_request("POST", "/proposals", json=payload)

    def list_messages(self, thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"thread_id": thread_id} if thread_id else {}
        return self._sync_request("GET", "/messages", params=params)

    def send_message(self, thread_id: str, recipient_id: str, content: str, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "thread_id": thread_id,
            "recipient_id": recipient_id,
            "content": content,
            "idempotency_key": idempotency_key
        }
        return self._sync_request("POST", "/messages", json=payload)
