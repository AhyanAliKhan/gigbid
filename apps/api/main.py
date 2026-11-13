"""
GigBid FastAPI Main Application Entrypoint
Mounts all routers: Auth, Jobs, Proposals, Approvals, Messages, Runs, Analytics, Settings.
Includes Degraded-Mode health reporting and Pipeline Board API.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from apps.api.routers import auth, jobs, proposals, approvals, messages, runs, analytics, settings
from agent.mcp_client import mcp_manager

app = FastAPI(
    title="GigBid Multi-Agent Copilot API",
    description="Backend API powering the GigBid multi-agent freelancer copilot.",
    version="1.0.0"
)

# Enable CORS for Next.js / React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all feature routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(proposals.router)
app.include_router(approvals.router)
app.include_router(messages.router)
app.include_router(runs.router)
app.include_router(analytics.router)
app.include_router(settings.router)

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    html_path = Path("apps/web/index.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return "<h1>GigBid API is running. UI file not found.</h1>"

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "gigbid-api",
        "version": "1.0.0",
        "degraded_mode": mcp_manager.degraded_mode,
        "queued_operations": len(mcp_manager.queued_operations)
    }

@app.get("/api/pipeline")
def get_pipeline_board():
    """Kanban Pipeline Board: Drafted, Submitted, Viewed, Replied, Interview, Hired, Lost."""
    return {
        "columns": [
            {
                "id": "drafted",
                "title": "Drafted",
                "cards": [
                    {"id": "c-01", "job_id": "job-0042", "title": "Production RAG Pipeline in PyTorch", "bid": 650.0, "client": "EnterpriseTech_01", "date": "Today"}
                ]
            },
            {
                "id": "submitted",
                "title": "Submitted",
                "cards": [
                    {"id": "c-02", "job_id": "job-0089", "title": "Next.js SaaS Dashboard Architecture", "bid": 550.0, "client": "Startup_08", "date": "Yesterday"}
                ]
            },
            {
                "id": "viewed",
                "title": "Viewed",
                "cards": [
                    {"id": "c-03", "job_id": "job-0112", "title": "Snowflake & dbt Enterprise Modeling", "bid": 720.0, "client": "DataCorp_12", "date": "2 days ago"}
                ]
            },
            {
                "id": "replied",
                "title": "Replied",
                "cards": [
                    {"id": "c-04", "job_id": "job-0145", "title": "High-Throughput FastAPI Microservice", "bid": 600.0, "client": "FintechGrowth_04", "date": "3 days ago"}
                ]
            },
            {
                "id": "interview",
                "title": "Interview",
                "cards": [
                    {"id": "c-05", "job_id": "job-0201", "title": "vLLM Low Latency Serving Cluster", "bid": 1200.0, "client": "AI_Scale_Labs", "date": "Scheduled for Tomorrow"}
                ]
            },
            {
                "id": "hired",
                "title": "Hired",
                "cards": [
                    {"id": "c-06", "job_id": "job-0005", "title": "Dockerized Agentic LangGraph Pipeline", "bid": 2400.0, "client": "AutonomousAI_Inc", "date": "Active Contract"}
                ]
            },
            {
                "id": "lost",
                "title": "Lost",
                "cards": [
                    {"id": "c-07", "job_id": "job-0033", "title": "Legacy COBOL Overhaul", "bid": 400.0, "client": "LegacyClient_02", "date": "Client hired internally"}
                ]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)
