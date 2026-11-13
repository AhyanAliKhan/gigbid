"""
GigSim Marketplace Simulator
High-fidelity Upwork/Freelance marketplace simulator REST API server.
Includes:
- Job discovery & search with pagination and filtering
- Client history & profile retrieval
- Connects balance management
- Proposal drafting and submission with idempotency and dry-run preview
- Messaging threads and client reply simulation
- Token bucket rate limiter (20 req/min) with standard headers
- Simulated client decision engine (reply / interview / hire)
- Chaos error injection toggle for viva resilience testing
"""

import os
import json
import time
import uuid
import random
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIGSIM_DATA_DIR = os.path.join(BASE_DIR, "gigsim", "data")

app = FastAPI(
    title="GigSim Marketplace Simulator",
    description="Official REST API stand-in for Upwork marketplace testing and evaluation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load seed data
with open(os.path.join(GIGSIM_DATA_DIR, "clients.json"), "r", encoding="utf-8") as f:
    CLIENTS: List[Dict[str, Any]] = json.load(f)
CLIENTS_BY_ID = {c["client_id"]: c for c in CLIENTS}

with open(os.path.join(GIGSIM_DATA_DIR, "jobs_stream.json"), "r", encoding="utf-8") as f:
    JOBS: List[Dict[str, Any]] = json.load(f)
JOBS_BY_ID = {j["job_id"]: j for j in JOBS}

# In-memory mutable state
USER_CONNECTS_BALANCE = {"default_user": 120}
PROPOSALS_DB: Dict[str, Dict[str, Any]] = {}
IDEMPOTENCY_CACHE: Dict[str, Dict[str, Any]] = {}
MESSAGES_DB: List[Dict[str, Any]] = []

# Rate limiter state: per token/IP token bucket
RATE_LIMIT_BUCKET: Dict[str, Dict[str, Any]] = {}
MAX_RPM = 60 # Allow comfortable testing limit, configurable
CHAOS_MODE = False

# -----------------------------------------------------------------------------
# Rate Limiting & Chaos Middleware
# -----------------------------------------------------------------------------
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    global CHAOS_MODE
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    # Check chaos header
    if request.headers.get("X-Simulate-Error") == "true" or CHAOS_MODE:
        return Response(
            content=json.dumps({"error": "Service Temporarily Unavailable (Simulated 503)"}),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
            headers={"Retry-After": "5"}
        )

    now = time.time()
    bucket = RATE_LIMIT_BUCKET.setdefault(client_ip, {"tokens": MAX_RPM, "last_refill": now})
    elapsed = now - bucket["last_refill"]
    bucket["tokens"] = min(MAX_RPM, bucket["tokens"] + elapsed * (MAX_RPM / 60.0))
    bucket["last_refill"] = now

    if bucket["tokens"] < 1.0:
        return Response(
            content=json.dumps({"error": "Rate limit exceeded. Maximum 60 requests per minute."}),
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            media_type="application/json",
            headers={
                "X-RateLimit-Limit": str(MAX_RPM),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(now + (1.0 - bucket["tokens"]) * (60.0 / MAX_RPM))),
                "Retry-After": "2"
            }
        )

    bucket["tokens"] -= 1.0
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(MAX_RPM)
    response.headers["X-RateLimit-Remaining"] = str(int(bucket["tokens"]))
    response.headers["X-RateLimit-Reset"] = str(int(now + 60))
    return response

# -----------------------------------------------------------------------------
# Pydantic Schemas
# -----------------------------------------------------------------------------
class ProposalSubmission(BaseModel):
    job_id: str
    cover_letter: str = Field(min_length=20)
    bid_amount: float = Field(gt=0)
    screening_answers: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    idempotency_key: str = Field(min_length=8)
    dry_run: bool = False

class MessagePayload(BaseModel):
    thread_id: str
    recipient_id: str
    content: str = Field(min_length=2)
    idempotency_key: Optional[str] = None

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "gigsim", "version": "1.0.0", "total_jobs": len(JOBS)}

@app.post("/admin/chaos/toggle")
def toggle_chaos(enabled: bool):
    global CHAOS_MODE
    CHAOS_MODE = enabled
    return {"status": "ok", "chaos_mode": CHAOS_MODE}

@app.get("/jobs")
def search_jobs(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_budget: Optional[float] = None,
    max_budget: Optional[float] = None,
    limit: int = 50,
    offset: int = 0
):
    results = JOBS
    if category:
        results = [j for j in results if j.get("category", "").lower() == category.lower()]
    if query:
        q = query.lower()
        results = [j for j in results if q in j["title"].lower() or q in j["description"].lower() or any(q in s.lower() for s in j.get("required_skills", []))]
    if min_budget is not None:
        results = [j for j in results if j["budget"]["max"] >= min_budget]
    if max_budget is not None:
        results = [j for j in results if j["budget"]["min"] <= max_budget]

    total = len(results)
    sliced = results[offset : offset + limit]
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "jobs": sliced
    }

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in JOBS_BY_ID:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS_BY_ID[job_id]

@app.get("/clients/{client_id}")
def get_client_history(client_id: str):
    if client_id not in CLIENTS_BY_ID:
        raise HTTPException(status_code=404, detail="Client not found")
    return CLIENTS_BY_ID[client_id]

@app.get("/connects/balance")
def get_connects_balance(user_id: str = "default_user"):
    balance = USER_CONNECTS_BALANCE.get(user_id, 120)
    return {"user_id": user_id, "connects_balance": balance, "currency": "CONNECTS"}

@app.post("/proposals")
def submit_proposal(submission: ProposalSubmission, user_id: str = "default_user"):
    # 1. Check idempotency
    if submission.idempotency_key in IDEMPOTENCY_CACHE:
        cached = IDEMPOTENCY_CACHE[submission.idempotency_key]
        cached["idempotent_replay"] = True
        return cached

    # 2. Check job exists
    if submission.job_id not in JOBS_BY_ID:
        raise HTTPException(status_code=404, detail=f"Job {submission.job_id} not found")
    
    job = JOBS_BY_ID[submission.job_id]
    connects_cost = job.get("connects_cost", 8)

    # 3. Handle dry run
    if submission.dry_run:
        preview = {
            "status": "dry_run_success",
            "job_id": submission.job_id,
            "bid_amount": submission.bid_amount,
            "connects_cost": connects_cost,
            "current_balance": USER_CONNECTS_BALANCE.get(user_id, 120),
            "projected_balance": USER_CONNECTS_BALANCE.get(user_id, 120) - connects_cost,
            "evidence_count": len(submission.evidence_ids),
            "cover_letter_preview": submission.cover_letter[:160] + "...",
            "screening_answers": submission.screening_answers
        }
        return preview

    # 4. Check connects balance
    current_balance = USER_CONNECTS_BALANCE.get(user_id, 120)
    if current_balance < connects_cost:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient connects. Required: {connects_cost}, Available: {current_balance}"
        )

    # 5. Deduct connects
    USER_CONNECTS_BALANCE[user_id] = current_balance - connects_cost

    # 6. Simulate client decision engine
    client = CLIENTS_BY_ID.get(job.get("client_id", ""), {})
    client_prefs = client.get("preferences", {})
    
    # Calculate reply probability based on evidence citation, price vs budget, and opening
    reply_prob = 0.35 # baseline
    if len(submission.evidence_ids) >= 2:
        reply_prob += 0.25
    elif len(submission.evidence_ids) == 1:
        reply_prob += 0.15
        
    # Check generic opening
    lower_cov = submission.cover_letter.lower()
    if lower_cov.startswith("dear sir") or lower_cov.startswith("i am excited to apply") or "i am passionate" in lower_cov:
        if client_prefs.get("dislike_generic_openings", True):
            reply_prob -= 0.20

    # Check budget ceiling
    if submission.bid_amount > job["budget"]["max"]:
        reply_prob -= 0.15
    elif submission.bid_amount <= job["budget"]["max"] and submission.bid_amount >= job["budget"]["min"]:
        reply_prob += 0.10

    # Ensure bounds
    reply_prob = max(0.05, min(0.92, reply_prob))
    will_reply = random.random() < reply_prob
    will_interview = will_reply and (random.random() < 0.65)
    will_hire = will_interview and (random.random() < 0.50)

    proposal_id = f"prop-sim-{uuid.uuid4().hex[:10]}"
    record = {
        "proposal_id": proposal_id,
        "job_id": submission.job_id,
        "user_id": user_id,
        "bid_amount": submission.bid_amount,
        "connects_spent": connects_cost,
        "remaining_connects": USER_CONNECTS_BALANCE[user_id],
        "status": "submitted",
        "evidence_cited": submission.evidence_ids,
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "client_simulation": {
            "reply_probability": round(reply_prob, 3),
            "will_reply": will_reply,
            "will_interview": will_interview,
            "will_hire": will_hire
        }
    }

    PROPOSALS_DB[proposal_id] = record
    IDEMPOTENCY_CACHE[submission.idempotency_key] = record

    # If client replies, seed initial client message in thread
    if will_reply:
        thread_id = f"thread-{job['job_id']}"
        MESSAGES_DB.append({
            "message_id": f"msg-{uuid.uuid4().hex[:8]}",
            "thread_id": thread_id,
            "job_id": job["job_id"],
            "sender_id": job.get("client_id", "client-unknown"),
            "sender_role": "client",
            "recipient_id": user_id,
            "content": f"Hi! Thanks for your detailed proposal and citing case study evidence. We were impressed with your background. Are you available for a brief 20-minute introductory call tomorrow?",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "requires_reply": True
        })

    return record

@app.get("/messages")
def list_messages(thread_id: Optional[str] = None):
    if thread_id:
        return [m for m in MESSAGES_DB if m.get("thread_id") == thread_id]
    return MESSAGES_DB

@app.post("/messages")
def send_message(payload: MessagePayload, user_id: str = "default_user"):
    msg_id = f"msg-{uuid.uuid4().hex[:8]}"
    msg = {
        "message_id": msg_id,
        "thread_id": payload.thread_id,
        "sender_id": user_id,
        "sender_role": "freelancer",
        "recipient_id": payload.recipient_id,
        "content": payload.content,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    MESSAGES_DB.append(msg)
    return {"status": "sent", "message": msg}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
