"""
Settings & Long-Term Memory Router
Manages autonomy levels, Connects budgets, and provides interactive visibility/deletion
of learned Style Memory and Outcome Memory.
"""

from fastapi import APIRouter
from agent.memory.store import memory_store
from apps.api.schemas.api_models import SettingsUpdateRequest, DeleteMemoryRuleRequest

router = APIRouter(prefix="/api/settings", tags=["settings"])

CURRENT_SETTINGS = {
    "autonomy_level": "semi_autonomous",
    "auto_skip_threshold": 0.35,
    "weekly_connects_budget": 120,
    "rate_floor_usd": 40.0,
    "connected_platforms": {
        "gigsim": {"status": "connected", "mode": "simulator", "url": "http://localhost:8081"},
        "upwork": {"status": "ready", "mode": "official_mcp", "oauth": "configured"}
    }
}

@router.get("/")
def get_settings():
    style_rules = memory_store.get_style_rules("default_user")
    return {
        "settings": CURRENT_SETTINGS,
        "style_memory_rules": style_rules,
        "outcome_memory": {
            "AI/ML": memory_store.get_outcome_memories("AI/ML"),
            "Full-Stack Web": memory_store.get_outcome_memories("Full-Stack Web"),
            "Data Analytics": memory_store.get_outcome_memories("Data Analytics")
        }
    }

@router.post("/update")
def update_settings(req: SettingsUpdateRequest):
    CURRENT_SETTINGS["autonomy_level"] = req.autonomy_level
    CURRENT_SETTINGS["auto_skip_threshold"] = req.auto_skip_threshold
    CURRENT_SETTINGS["weekly_connects_budget"] = req.weekly_connects_budget
    CURRENT_SETTINGS["rate_floor_usd"] = req.rate_floor_usd
    return {"status": "updated", "settings": CURRENT_SETTINGS}

@router.delete("/memory/{rule_id}")
def delete_memory_rule(rule_id: str):
    success = memory_store.delete_style_rule("default_user", rule_id)
    return {"status": "deleted" if success else "not_found", "rule_id": rule_id}
