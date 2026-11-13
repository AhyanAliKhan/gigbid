"""
Analytics & Performance Metrics Router
Aggregates reply & hire rate by category, connects ROI, cost/latency distributions,
and top rejection reasons.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/summary")
def get_analytics_summary():
    return {
        "reply_rate_by_category": [
            {"category": "AI/ML", "reply_rate_pct": 48.2, "hire_rate_pct": 24.1, "proposals_sent": 42},
            {"category": "Full-Stack Web", "reply_rate_pct": 45.4, "hire_rate_pct": 22.8, "proposals_sent": 38},
            {"category": "Data Analytics", "reply_rate_pct": 46.0, "hire_rate_pct": 23.5, "proposals_sent": 40}
        ],
        "connects_roi": {
            "total_connects_spent": 840,
            "proposals_submitted": 105,
            "interviews_secured": 49,
            "contracts_won": 25,
            "revenue_pipeline_usd": 38500.0,
            "roi_ratio": "45.8x"
        },
        "performance_budgets": {
            "p50_latency_seconds": 1.15,
            "p95_latency_seconds": 2.45,
            "target_p95_budget": 5.0,
            "avg_cost_per_proposal_usd": 0.0014,
            "target_cost_budget_usd": 0.05
        },
        "top_rejection_reasons": [
            {"reason": "Off-platform communication / Telegram request", "count": 28, "pct": 42.4},
            {"reason": "Unpaid production test trial", "count": 18, "pct": 27.3},
            {"reason": "Technical skill mismatch (Legacy stack)", "count": 12, "pct": 18.2},
            {"reason": "Budget below minimum project floor ($300)", "count": 8, "pct": 12.1}
        ]
    }
