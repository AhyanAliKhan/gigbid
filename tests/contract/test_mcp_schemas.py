"""
MCP Contract Schema Snapshot Tests
Verifies that tool input schemas, validation bounds, and output annotations do not drift unintentionally.
"""

import pytest
from pydantic import ValidationError
from mcp_servers.marketplace.server import (
    SearchJobsInput,
    GetJobInput,
    SubmitProposalInput,
    CreateProposalDraftInput,
    SendMessageInput
)

def test_search_jobs_contract():
    # Valid
    inp = SearchJobsInput(query="Python", limit=10, offset=0)
    assert inp.limit == 10
    
    # Boundary violations
    with pytest.raises(ValidationError):
        SearchJobsInput(limit=0) # ge=1
    with pytest.raises(ValidationError):
        SearchJobsInput(limit=500) # le=100

def test_submit_proposal_contract_constraints():
    # Valid
    inp = SubmitProposalInput(
        job_id="job-001",
        cover_letter="Valid proposal cover letter with sufficient length for review.",
        bid_amount=350.0,
        idempotency_key="idemp-key-12345"
    )
    assert inp.bid_amount == 350.0
    
    # Short cover letter (< 20 chars)
    with pytest.raises(ValidationError):
        SubmitProposalInput(
            job_id="job-001",
            cover_letter="Too short",
            bid_amount=350.0,
            idempotency_key="idemp-key-12345"
        )
    
    # Non-positive bid amount (<= 0)
    with pytest.raises(ValidationError):
        SubmitProposalInput(
            job_id="job-001",
            cover_letter="Valid proposal cover letter with sufficient length for review.",
            bid_amount=-50.0,
            idempotency_key="idemp-key-12345"
        )
    
    # Short idempotency key (< 8 chars)
    with pytest.raises(ValidationError):
        SubmitProposalInput(
            job_id="job-001",
            cover_letter="Valid proposal cover letter with sufficient length for review.",
            bid_amount=350.0,
            idempotency_key="short"
        )

def test_send_message_contract_constraints():
    # Valid
    msg = SendMessageInput(
        thread_id="thread-01",
        recipient_id="client-01",
        content="Hello, thank you for reaching out.",
        idempotency_key="idemp-key-99887"
    )
    assert msg.content == "Hello, thank you for reaching out."

    # Empty content
    with pytest.raises(ValidationError):
        SendMessageInput(
            thread_id="thread-01",
            recipient_id="client-01",
            content="",
            idempotency_key="idemp-key-99887"
        )
