# GigBid Operational Runbook & Guide

This runbook outlines operational procedures for deploying, maintaining, and troubleshooting the GigBid autonomous copilot.

---

## 1. System Requirements & Environment Setup

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js 18+ & npm
- Git

### Installation
```bash
# 1. Clone repository
git clone https://github.com/AhyanAliKhan/gigbid.git
cd gigbid

# 2. Set up virtual environment
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Frontend dependencies
cd apps/web
npm install
cd ../..
```

---

## 2. Launching System Services

### A. Start Marketplace Simulator (`GigSim`)
```bash
uvicorn gigsim.server:app --host 0.0.0.0 --port 8001 --reload
```
- Available at `http://localhost:8001`
- OpenAPI docs: `http://localhost:8001/docs`

### B. Start FastAPI Application Backend
```bash
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base: `http://localhost:8000`
- Interactive Swagger: `http://localhost:8000/docs`

### C. Start React Frontend (Vite)
```bash
cd apps/web
npm run dev
```
- Web Application: `http://localhost:5173`

### D. Start Autonomous Background Worker & Scout
```bash
python worker/scheduler.py
```
- Polls marketplace feeds every 60s
- Checkpoints state to `data/worker_state.json`
- Stops gracefully on `Ctrl+C`

---

## 3. Operations & Degraded Mode Procedures

### Rate Limits & Connects Budgets
- **Connects Budget**: Configured via `worker/scheduler.py` (`max_daily_bids=15`, `connects_budget=100`).
- **Idempotency**: All bid submissions carry an idempotency key `hash(job_id + persona_id)`. Re-submitting a previously bid job returns the cached receipt with HTTP 200 without deducting connects.
- **Chaos & Rate Limit Testing**: Toggle chaos mode in GigSim via `POST /sim/chaos` to test 429 rate limit backoff and network failures.

### Degraded Mode Recovery
- If the Portfolio MCP server becomes unreachable, `MultiServerMCPManager` raises `DegradedModeError`.
- The system automatically falls back to local persona JSON files (`data/personas/<persona_id>/profile.json`).
- The Web UI displays a prominent banner: `DEGRADED MODE ACTIVE: Portfolio MCP unreachable. Using cached profile.`
- Once the MCP server is restored, the client automatically re-establishes SSE connectivity and clears the banner.

---

## 4. Running Tests & Evaluations

### Automated Test Suite
```bash
# Run all unit, contract, and integration tests
pytest -v tests/

# Run specific test suites
pytest -v tests/unit/test_mcp_servers.py
pytest -v tests/contract/test_mcp_schemas.py
pytest -v tests/unit/test_rag.py
pytest -v tests/integration/test_bid_graph.py
pytest -v tests/integration/test_crash_resume.py
pytest -v tests/unit/test_api_endpoints.py
```

### End-to-End (E2E) Playwright Tests
```bash
cd apps/web
npx playwright test
```

### Evaluation Benchmark Runners
```bash
# Part A: Tool Design Evaluation (Fine vs Coarse vs Optimized)
python evals/runners/tool_design_eval.py

# Part B: Judge Calibration (Cohen's Kappa)
python evals/runners/judge_calibration.py

# Part B: RAG Benchmark Across 600 Jobs
python evals/runners/rag_eval.py

# Part B: RAG Ablation Study
python evals/runners/ablation.py

# Part C: Multi-Agent Architecture Comparison (50 Jobs)
python evals/runners/multiagent_comparison.py

# Part E: Prompt Injection Defense Benchmark (25 Attacks)
python evals/runners/injection_eval.py

# Extension X2: Proposal A/B Experimentation (100 Jobs)
python evals/runners/ab_test_experiment.py
```

All benchmark artifacts and CSV reports are written directly to `evals/results/`.
