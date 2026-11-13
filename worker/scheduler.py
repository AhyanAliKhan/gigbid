"""
Background Worker & Autonomous Scout Scheduler for GigBid
Polls marketplace adapters periodically, runs Bid Graph on new job listings,
tracks connects budget, and maintains execution state with crash recovery.
"""

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Set, Optional

from agent.graphs.bid_graph import build_bid_graph, bid_graph
from agent.mcp_client import MultiServerMCPManager, mcp_manager
from gigsim.server import JOBS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Worker] %(message)s"
)
logger = logging.getLogger("GigBidScheduler")

STATE_FILE = Path("data/worker_state.json")


class GigBidScheduler:
    def __init__(
        self,
        persona_id: str = "alex_chen_aiml",
        poll_interval_seconds: int = 60,
        max_daily_bids: int = 15,
        connects_budget: int = 100,
        auto_approve_threshold: float = 0.95,
        dry_run: bool = True
    ):
        self.persona_id = persona_id
        self.poll_interval = poll_interval_seconds
        self.max_daily_bids = max_daily_bids
        self.connects_budget = connects_budget
        self.auto_approve_threshold = auto_approve_threshold
        self.dry_run = dry_run
        
        self.is_running = False
        self.processed_job_ids: Set[str] = set()
        self.bids_submitted_today = 0
        self.active_runs: Dict[str, Any] = {}
        self.daily_reset_date = datetime.now(timezone.utc).date()
        
        # Initialize LangGraph & MCP Client
        self.mcp_client = mcp_manager
        self.bid_graph = bid_graph
        
        self._load_state()

    def _load_state(self):
        """Restore processed jobs and run counters from disk."""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.processed_job_ids = set(data.get("processed_job_ids", []))
                    self.bids_submitted_today = data.get("bids_submitted_today", 0)
                    last_date_str = data.get("last_date")
                    if last_date_str:
                        last_date = datetime.fromisoformat(last_date_str).date()
                        if last_date < datetime.now(timezone.utc).date():
                            self.bids_submitted_today = 0
                logger.info(f"Loaded state: {len(self.processed_job_ids)} processed jobs, {self.bids_submitted_today} bids today.")
            except Exception as e:
                logger.warning(f"Could not load worker state: {e}")

    def _save_state(self):
        """Persist processed jobs and counters to disk."""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "processed_job_ids": list(self.processed_job_ids),
                    "bids_submitted_today": self.bids_submitted_today,
                    "last_date": datetime.now(timezone.utc).isoformat(),
                    "connects_budget": self.connects_budget
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist worker state: {e}")

    def _check_daily_reset(self):
        current_date = datetime.now(timezone.utc).date()
        if current_date > self.daily_reset_date:
            self.daily_reset_date = current_date
            self.bids_submitted_today = 0
            logger.info("New day detected: Daily bid limit reset.")

    async def fetch_marketplace_jobs(self) -> List[Dict[str, Any]]:
        """Fetch latest open jobs from marketplace simulator or live adapter."""
        try:
            recent_jobs = JOBS[:25]
            return [
                j for j in recent_jobs 
                if j["job_id"] not in self.processed_job_ids
            ]
        except Exception as e:
            logger.error(f"Error fetching marketplace jobs: {e}")
            return []

    async def process_job(self, job: Dict[str, Any]):
        """Run the multi-agent BidGraph pipeline on a newly discovered job."""
        job_id = job["job_id"]
        self.processed_job_ids.add(job_id)
        
        if self.bids_submitted_today >= self.max_daily_bids:
            logger.warning(f"Daily bid limit ({self.max_daily_bids}) reached. Skipping job {job_id}.")
            return

        logger.info(f"==> Processing job {job_id}: '{job.get('title')}'")
        
        # Initial state setup
        initial_state = {
            "thread_id": f"worker-run-{job_id}",
            "job_id": job_id,
            "persona_id": self.persona_id,
            "job_spec": None,
            "risk_report": None,
            "fit_report": None,
            "bid_decision": None,
            "proposal_draft": None,
            "claim_evidence": [],
            "critique": None,
            "critique_rounds": 0,
            "compliance_verdict": None,
            "human_approval": None,
            "submission_receipt": None,
            "status": "scouting",
            "messages": [],
            "errors": [],
            "step_count": 0,
            "total_tokens_used": 0,
            "metadata": {"source": "scheduler_worker", "dry_run": self.dry_run}
        }
        
        config = {"configurable": {"thread_id": f"worker-run-{job_id}"}}
        
        try:
            # Execute graph until completion or interrupt gate
            result = await self.bid_graph.ainvoke(initial_state, config=config)
            
            status = result.get("status")
            logger.info(f"Job {job_id} reached status: {status}")
            
            # Check if paused at human approval gate
            if status == "awaiting_approval":
                logger.info(f"[INTERRUPT] Job {job_id} is awaiting human approval in Proposal Studio.")
                self.active_runs[job_id] = {
                    "thread_id": result.get("thread_id"),
                    "job_title": job.get("title"),
                    "proposal": result.get("proposal_draft", {}).get("cover_letter", "")[:100] + "...",
                    "price": result.get("bid_decision", {}).get("proposed_budget", 0),
                    "status": "awaiting_approval",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            elif status == "submitted":
                self.bids_submitted_today += 1
                logger.info(f"[SUBMITTED] Proposal for job {job_id} submitted successfully!")
            elif status == "skipped":
                reason = result.get("bid_decision", {}).get("reason", "Low fit or high risk")
                logger.info(f"[SKIPPED] Job {job_id} skipped: {reason}")
                
        except Exception as e:
            logger.error(f"Error executing BidGraph on {job_id}: {e}", exc_info=True)
            
        self._save_state()

    async def run_loop(self):
        """Continuous execution loop."""
        self.is_running = True
        logger.info(f"Worker scheduler started. Polling every {self.poll_interval}s. DryRun={self.dry_run}")
        
        while self.is_running:
            self._check_daily_reset()
            try:
                new_jobs = await self.fetch_marketplace_jobs()
                if new_jobs:
                    logger.info(f"Discovered {len(new_jobs)} unprocessed marketplace jobs.")
                    for job in new_jobs:
                        if not self.is_running:
                            break
                        await self.process_job(job)
                        # Brief throttle between job evaluations
                        await asyncio.sleep(2)
                else:
                    logger.debug("No new jobs in current polling interval.")
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {e}")
                
            await asyncio.sleep(self.poll_interval)

    def stop(self):
        """Signal worker to stop gracefully."""
        logger.info("Stopping worker scheduler...")
        self.is_running = False
        self._save_state()


async def main():
    scheduler = GigBidScheduler(
        persona_id="alex_chen_aiml",
        poll_interval_seconds=30,
        max_daily_bids=10,
        dry_run=True
    )
    
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, scheduler.stop)
        except NotImplementedError:
            pass  # Windows event loop limitation
            
    try:
        await scheduler.run_loop()
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main())
