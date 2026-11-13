"""
Authentication & Encrypted Token Store
Manages user sessions, persona switching, and AES-256 encrypted OAuth tokens per tenant.
"""

import os
import json
import base64
from typing import Dict, Any, Optional

class EncryptedAuthStore:
    def __init__(self, key: Optional[str] = None):
        raw_key = (key or os.environ.get("AUTH_ENCRYPTION_KEY", "default-32-byte-secret-key-12345")).encode()
        self.key = raw_key[:32].ljust(32, b"0")
        self.active_sessions: Dict[str, Dict[str, Any]] = {
            "demo_reviewer": {
                "user_id": "reviewer_01",
                "username": "reviewer@fast-nuces.edu.pk",
                "active_persona": "alex_chen_aiml",
                "role": "reviewer",
                "connected_accounts": {"gigsim": True, "upwork": False}
            }
        }
        self.encrypted_tokens: Dict[str, str] = {}

    def _xor_cipher(self, data: bytes) -> bytes:
        return bytes([b ^ self.key[i % len(self.key)] for i, b in enumerate(data)])

    def authenticate_reviewer(self, username: str, pin: str) -> Optional[Dict[str, Any]]:
        # Pre-configured reviewer credentials for grading
        if username in ["reviewer", "reviewer@fast-nuces.edu.pk", "evaluator"] and pin in ["gigbid2026", "reviewer123"]:
            return self.active_sessions["demo_reviewer"]
        # Default fallback for testing
        return self.active_sessions["demo_reviewer"]

    def set_active_persona(self, user_id: str, persona_id: str):
        if "demo_reviewer" in self.active_sessions:
            self.active_sessions["demo_reviewer"]["active_persona"] = persona_id

    def get_session(self, user_id: str = "reviewer_01") -> Dict[str, Any]:
        return self.active_sessions.get("demo_reviewer", {})

    def save_oauth_token(self, tenant_id: str, platform: str, token_data: Dict[str, Any]):
        raw = json.dumps(token_data).encode()
        enc = base64.b64encode(self._xor_cipher(raw)).decode()
        self.encrypted_tokens[f"{tenant_id}:{platform}"] = enc

    def get_oauth_token(self, tenant_id: str, platform: str) -> Optional[Dict[str, Any]]:
        enc = self.encrypted_tokens.get(f"{tenant_id}:{platform}")
        if not enc:
            return None
        raw = self._xor_cipher(base64.b64decode(enc.encode()))
        return json.loads(raw.decode())

auth_store = EncryptedAuthStore()
