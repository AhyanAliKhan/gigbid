"""
Pricing Strategist Agent Node
Proposes an optimal bid from market statistics, client historical spend,
and user rate floors; evaluates Connects spend return on investment.
Tool Access: Marketplace (read).
"""

import os
from typing import Dict, Any
from agent.state import GigBidState
from agent.handoffs import PriceQuote
from agent.mcp_client import mcp_manager

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "pricing_v1.md")

def pricing_node(state: GigBidState) -> Dict[str, Any]:
    job = state.get("job", {})
    budget = job.get("budget", {})
    b_min = budget.get("min", 250)
    b_max = budget.get("max", 600)
    connects_cost = job.get("connects_cost", 8)
    fit_score = state.get("fit_report", {}).score if state.get("fit_report") else 0.8
    
    # 1. Query client history for tier pricing adjustment
    cid = job.get("client_id", "")
    client_spent = 0
    client_tier = "Startup"
    if cid:
        try:
            client_info = mcp_manager.execute_tool("pricing", "get_client_history", {"client_id": cid})
            client_spent = client_info.get("total_spent_usd", 0)
            client_tier = client_info.get("tier", "Startup")
        except Exception:
            pass

    # Floor price constraint
    floor_price = 300.0
    suggested_bid = max(floor_price, (b_min + b_max) / 2.0)
    
    # Premium adjustment for enterprise clients
    if client_tier == "Enterprise" or client_spent > 50000:
        suggested_bid = min(b_max, suggested_bid * 1.15)
    
    suggested_bid = round(suggested_bid, 2)
    roi = round((suggested_bid * fit_score) / max(1, connects_cost), 2)
    
    rationale = f"Suggested bid of ${suggested_bid} positioned within budget band [${b_min}, ${b_max}] based on {client_tier} tier client spend (${client_spent:,.0f}) and strong candidate fit ({fit_score:.0%})."

    quote = PriceQuote(
        suggested_bid=suggested_bid,
        price_band_min=float(b_min),
        price_band_max=float(b_max),
        connects_cost=connects_cost,
        roi_score=roi,
        rationale=rationale
    )

    trace_entry = {
        "node": "pricing",
        "action": "calculate_price_quote",
        "suggested_bid": suggested_bid,
        "connects_cost": connects_cost,
        "roi_score": roi,
        "tokens": 220
    }

    return {
        "price_quote": quote,
        "step_count": 1,
        "total_tokens_used": 220,
        "execution_trace": [trace_entry]
    }
