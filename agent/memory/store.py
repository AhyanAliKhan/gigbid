"""
GigBid Long-Term Memory Store
Manages persistent memories in separate namespaces:
1. style_memory: Learned from user's manual edits to drafts via explicit promotion rules.
2. outcome_memory: Learned from verified winning and replied proposals by job category.
Raw agent outputs and raw tool calls NEVER enter memory directly.
"""

import os
import json
import time
import uuid
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "long_term_memory.json")

class LongTermMemoryStore:
    def __init__(self, storage_path: Optional[str] = None):
        self.path = storage_path or MEMORY_FILE
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            initial_data = {
                "style_memory": {
                    "default_user": [
                        {
                            "rule_id": "style-001",
                            "rule": "Never include introductory greetings like 'I am passionate' or 'Dear Sir/Madam'.",
                            "evidence": "Promoted after user deleted greeting in 3 consecutive drafts.",
                            "occurrences": 3,
                            "promoted_at": "2026-11-01T10:00:00Z"
                        },
                        {
                            "rule_id": "style-002",
                            "rule": "Always cite past metrics with explicit percentage improvements before discussing timeline.",
                            "evidence": "Promoted from user edit diffs on technical proposals.",
                            "occurrences": 2,
                            "promoted_at": "2026-11-05T14:30:00Z"
                        }
                    ]
                },
                "outcome_memory": {
                    "AI/ML": [
                        {
                            "memory_id": "out-aiml-01",
                            "pattern": "Proposals citing low-latency inference benchmarks achieved 48% higher reply rate.",
                            "sample_size": 35,
                            "promoted_at": "2026-11-02T12:00:00Z"
                        }
                    ],
                    "Full-Stack Web": [
                        {
                            "memory_id": "out-fs-01",
                            "pattern": "Proposals providing live deployment links and test coverage metrics achieved 52% hire rate.",
                            "sample_size": 40,
                            "promoted_at": "2026-11-03T16:00:00Z"
                        }
                    ],
                    "Data Analytics": [
                        {
                            "memory_id": "out-da-01",
                            "pattern": "Proposals emphasizing automated ETL and Snowflake query cost reductions won 44% of bids.",
                            "sample_size": 38,
                            "promoted_at": "2026-11-04T11:00:00Z"
                        }
                    ]
                }
            }
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _read_data(self) -> Dict[str, Any]:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_data(self, data: Dict[str, Any]):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_style_rules(self, user_id: str = "default_user") -> List[Dict[str, Any]]:
        data = self._read_data()
        return data.get("style_memory", {}).get(user_id, [])

    def add_style_rule(self, user_id: str, rule: str, evidence: str) -> Dict[str, Any]:
        data = self._read_data()
        user_rules = data.setdefault("style_memory", {}).setdefault(user_id, [])
        new_rule = {
            "rule_id": f"style-{uuid.uuid4().hex[:6]}",
            "rule": rule,
            "evidence": evidence,
            "occurrences": 2,
            "promoted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        user_rules.append(new_rule)
        self._write_data(data)
        return new_rule

    def delete_style_rule(self, user_id: str, rule_id: str) -> bool:
        data = self._read_data()
        user_rules = data.get("style_memory", {}).get(user_id, [])
        initial_len = len(user_rules)
        data["style_memory"][user_id] = [r for r in user_rules if r.get("rule_id") != rule_id]
        if len(data["style_memory"][user_id]) < initial_len:
            self._write_data(data)
            return True
        return False

    def get_outcome_memories(self, category: str) -> List[Dict[str, Any]]:
        data = self._read_data()
        return data.get("outcome_memory", {}).get(category, [])

    def promote_outcome_memory(self, category: str, pattern: str, sample_size: int) -> Dict[str, Any]:
        data = self._read_data()
        cat_mems = data.setdefault("outcome_memory", {}).setdefault(category, [])
        new_mem = {
            "memory_id": f"out-{uuid.uuid4().hex[:6]}",
            "pattern": pattern,
            "sample_size": sample_size,
            "promoted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        cat_mems.append(new_mem)
        self._write_data(data)
        return new_mem

memory_store = LongTermMemoryStore()
