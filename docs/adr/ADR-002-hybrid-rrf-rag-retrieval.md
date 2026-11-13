# ADR-002: Hybrid BM25 + Dense RRF for Evidence Retrieval

## Status
Accepted

## Context
Marketplace job descriptions combine precise technical tokens (e.g. `PyTorch 2.2`, `FastAPI`, `WebSockets`) with broad semantic context (e.g., "high throughput real-time streaming backend"). Pure dense semantic retrieval frequently misses critical exact-match keywords, while pure BM25 fails to match conceptual equivalents.

## Decision
We select **V2 Hybrid Retrieval with Reciprocal Rank Fusion (RRF)**:
- Sparse search via Okapi BM25 index over portfolio case studies.
- Dense retrieval using TF-IDF n-gram vectors.
- Rank combination via standard RRF formula with $k=60$:
  $$RRF(d) = \frac{1}{60 + \text{rank}_{\text{BM25}}(d)} + \frac{1}{60 + \text{rank}_{\text{Dense}}(d)}$$

## Consequences
- **Positive**: High Recall@5 (0.478 vs 0.333 baseline), sub-second p95 latency (0.98s), robust to out-of-vocabulary acronyms.
- **Negative**: Requires maintaining two index structures in memory.
