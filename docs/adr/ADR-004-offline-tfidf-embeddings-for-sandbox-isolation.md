# ADR-004: Offline TF-IDF Dense Embeddings for Isolated Sandbox Environments

## Status
Accepted

## Context
Deploying neural embedding models (e.g. HuggingFace `all-MiniLM-L6-v2`) requires downloading multi-hundred-megabyte weight files at runtime. In secure enterprise sandboxes, continuous integration runners, or air-gapped evaluation environments without external internet access, model loading fails with socket connection errors.

## Decision
We utilize scikit-learn's `TfidfVectorizer` configured with sublinear term-frequency scaling and character/word n-grams `(1, 2)` to generate 1024-dimensional dense vectors:
- 100% self-contained in standard Python wheels (`scikit-learn`).
- Deterministic vector generation with zero network overhead.
- Ultra-fast index building and query vectorization ($<5$ ms).

## Consequences
- **Positive**: Complete offline autonomy, zero external model weights to download, zero latency flakiness in automated testing.
- **Negative**: Semantic similarity is bounded by lexical n-gram co-occurrence compared to 384-d transformer representations.
