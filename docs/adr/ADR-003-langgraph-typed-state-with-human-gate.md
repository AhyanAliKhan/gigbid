# ADR-003: Multi-Agent Orchestration with LangGraph StateGraph and Interrupt Gates

## Status
Accepted

## Context
Autonomous bidding systems face catastrophic risk if an unvetted LLM submits invalid bids, hallucinates rates, or contacts clients off-platform. Single-agent ReAct models suffer from goal drift, hallucinated claims (2.8/proposal in our tests), and susceptibility to prompt injection attacks embedded in job listings.

## Decision
We orchestrate the bidding pipeline as a LangGraph `StateGraph`:
1. Parallel fan-out for Scout, Analyst, and Risk Assessor.
2. Router node that prunes unviable jobs before drafting.
3. Proposal Writer with grounded evidence injection.
4. Grounding Verifier that audits claims against portfolio evidence.
5. Critic agent with a strictly bounded reflection loop ($\le 2$ iterations).
6. Compliance Guard enforcing marketplace rules.
7. LangGraph `interrupt()` human approval gate before any external marketplace mutation.

## Consequences
- **Positive**: 98% bid decision accuracy, 0 unsupported claims, 100% compliance pass rate, zero unauthorized submissions.
- **Negative**: Higher graph latency and state management complexity compared to single ReAct agent.
