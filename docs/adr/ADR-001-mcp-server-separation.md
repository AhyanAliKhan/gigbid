# ADR-001: Separation of Concerns Across Dedicated MCP Servers

## Status
Accepted

## Context
An autonomous freelancing agent must interact with heterogeneous external systems: personal portfolio archives, commercial job marketplaces (Upwork, Freelancer), and workspace productivity tools (Calendar, Email). Integrating all capabilities into a single monolithic API creates severe privilege creep, makes credential rotation hazardous, and complicates testing.

## Decision
We implement three distinct Model Context Protocol (MCP) servers:
1. `mcp_servers/portfolio`: Read-only access to CVs, case studies, repository code, and testimonials.
2. `mcp_servers/marketplace`: Read access to job postings and client histories; write access to proposal submission (strictly gated).
3. `mcp_servers/workspace`: Calendar slot holds and draft email composition.

Furthermore, we enforce agent-level allowlists in `MultiServerMCPManager` so that agents only receive tools relevant to their specific role.

## Consequences
- **Positive**: Strict isolation, reduced attack surface, testability via mock adapters (GigSim).
- **Negative**: Requires maintaining three server lifecycles and JSON-RPC / SSE connections.
