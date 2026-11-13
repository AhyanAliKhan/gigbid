# GigBid MCP Tool Inventory & Trust Rationales

This document records the complete specification of all internal and external Model Context Protocol (MCP) tools consumed across the GigBid multi-agent architecture.

## 1. Tool Directory & Schema Annotations

| Tool Name | Server | Read / Write | Annotations (MCP 2026) | Auth Mechanism | Primary Agent Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `search_evidence` | Portfolio | Read | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` | In-process / Local | Fit Matcher, Proposal Writer, Critic |
| `get_case_study` | Portfolio | Read | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` | In-process / Local | Fit Matcher, Proposal Writer |
| `list_skills` | Portfolio | Read | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` | In-process / Local | Fit Matcher |
| `search_jobs` | Marketplace | Read | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` | Bearer Token | Scout |
| `get_job` | Marketplace | Read | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` | Bearer Token | Scout, Risk Assessor |
| `get_client_history` | Marketplace | Read | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` | Bearer Token | Risk Assessor, Pricing Strategist |
| `get_connects_balance` | Marketplace | Read | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` | Bearer Token | Pricing Strategist |
| `create_proposal_draft` | Marketplace | Write | `readOnlyHint: false`, `destructiveHint: false`, `idempotentHint: true` | Bearer Token | Proposal Studio (Preview) |
| `submit_proposal` | Marketplace | Write | `readOnlyHint: false`, `destructiveHint: true`, `idempotentHint: true` | Bearer Token + Human Approval | Marketplace Submitter |
| `list_messages` | Marketplace | Read | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` | Bearer Token | Client Liaison |
| `send_message` | Marketplace | Write | `readOnlyHint: false`, `destructiveHint: false`, `idempotentHint: true` | Bearer Token + Human Approval | Client Liaison |
| `get_free_calendar_slots` | Workspace | Read | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` | OAuth2 / Local Mock | Client Liaison |
| `create_tentative_interview_hold` | Workspace | Write | `readOnlyHint: false`, `destructiveHint: false`, `idempotentHint: true` | OAuth2 / Local Mock | Client Liaison |
| `create_email_draft` | Workspace | Write | `readOnlyHint: false`, `destructiveHint: false`, `idempotentHint: true` | OAuth2 / Local Mock | Client Liaison |

---

## 2. Third-Party Server Trust Rationales

1. **Official Upwork MCP Server (`https://mcp.upwork.com/mcp`)**:
   - *Trust Rationale:* First-party server maintained by Upwork with OAuth 2.1 authorization; guarantees compliance with Upwork automation terms of service by enforcing that all proposal and contract writes remain private drafts requiring user confirmation.
2. **Official GitHub MCP Server (`github/github-mcp-server`)**:
   - *Trust Rationale:* Read-only token scoped strictly to the freelancer's public portfolio repositories; ingests code repositories and READMEs without granting write permissions to production repositories.

---

## 3. Client Discipline & Allowlist Policy

To mitigate unauthorized cross-talk and prompt-injection tool hijacking, every LangGraph node has an immutable tool allowlist enforced by `agent/mcp_client.py`:
- `scout`: `[search_jobs, get_job]`
- `analyst`: `[]` (pure extraction, zero external tools)
- `risk_assessor`: `[get_job, get_client_history]`
- `fit_matcher`: `[search_evidence, get_case_study, list_skills]`
- `pricing`: `[get_client_history, get_connects_balance]`
- `writer`: `[search_evidence, get_case_study]`
- `verifier`: `[search_evidence, get_case_study]`
- `critic`: `[search_evidence, get_case_study]`
- `compliance`: `[]` (pure policy check, zero external tools)
- `client_liaison`: `[list_messages, send_message, get_free_calendar_slots, create_tentative_interview_hold, create_email_draft]`
