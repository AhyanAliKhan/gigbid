# AI Usage Disclosure & Failure Accountability Log

## 1. Transparency Disclosure
In accordance with academic integrity guidelines for AI-4016, this document discloses the utilization of AI coding assistants during the research, architecture, implementation, and benchmarking of **GigBid**.

### Tools & Models Employed
- **Antigravity AI (Google DeepMind)**: Assisted in scaffolding boilerplate, running automated evals, implementing LangGraph typed states, configuring MCP servers, writing unit tests, and compiling documentation.
- **Underlying Models**: Gemini 2.5 Pro / Flash.

---

## 2. Prompts & Workflow Patterns
Key prompt archetypes utilized during development:
1. **Tool Definition & Schema Contracts**: Translating marketplace and portfolio interface specifications into strict Pydantic models with runtime validators.
2. **Evaluation Harness Design**: Structuring statistical benchmark runners (Cohen's Kappa calculation, two-proportion Z-tests, Reciprocal Rank Fusion ranking).
3. **Graph Reducer Debugging**: Resolving state update collisions across parallel LangGraph branches.

---

## 3. Failure & Bug Accountability Log

The table below catalogs real failures, validation errors, and runtime bugs encountered during engineering, their detection mechanism, and the architectural fix implemented:

| Bug # | Component | Failure Description | Detection Method | Root Cause | Architectural Resolution |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **01** | `agent/state.py` | `InvalidUpdateError: At key 'step_count': Can receive only one value per step` | Integration Test (`test_bid_graph.py`) | Parallel fan-out branches returned un-reduced writes to primitive int and str fields. | Implemented typed reducers (`operator.add` for counters/tokens, `reduce_last` for status, `reduce_list` for evidence). |
| **02** | `rag/verify.py` | Cover letter validation error: `cover_letter too short (<50 words)` | Contract Test (`test_bid_graph.py`) | Grounding verifier completely excised unsupported sentences without replacement. | Modified verifier to rewrite ungrounded assertions into general claims citing verified case study IDs. |
| **03** | `rag/index/vector_index.py` | `getaddrinfo failed` when instantiating `SentenceTransformer("all-MiniLM-L6-v2")` | RAG Eval Runner (`rag_eval.py`) | Offline sandbox environment blocked external downloads from HuggingFace Hub. | Re-architected dense retriever to use 1024-dimensional TF-IDF character n-gram vectors computed 100% offline. |
| **04** | `mcp_servers/` | `ModuleNotFoundError: mcp.server.fastmcp` | Unit Test (`test_mcp_servers.py`) | MCP Python SDK 2.x renamed internal modules to `MCPServer`. | Updated import to `from mcp.server.mcpserver import MCPServer` matching official MCP SDK v2. |
| **05** | `agent/mcp_client.py` | `ImportError: cannot import name 'PermissionError'` | Unit Test | Standard library `PermissionError` was shadowed by module namespace. | Defined custom domain exception `ClientDisciplineError(MCPExecutionError)`. |
| **06** | `rag/variants/v0_naive.py` | `TypeError: retrieve() missing 1 required positional argument: 'job_description'` | Benchmark Runner (`rag_eval.py`) | Inconsistent retriever signature between `v0_naive.py` and `v2_hybrid.py`. | Standardized all retriever variant interfaces to accept optional keyword arguments `(query, job_description, top_k)`. |
| **07** | `evals/runners/ab_test.py` | `TypeError: float() argument must be a string or a real number, not 'dict'` | Experiment Runner (`ab_test_experiment.py`) | Job dataset contained structured budget dicts `{'min': 1111, 'max': 2010}` instead of scalar floats. | Added safe extraction helper `extract_budget()` handling both nested dicts and numeric scalars. |
| **08** | `evals/runners/ab_test.py` | `TypeError: Object of type bool is not JSON serializable` | Experiment Runner (`ab_test_experiment.py`) | SciPy / Python 3.14 comparison yielded numpy-typed boolean flags that failed `json.dump`. | Explicitly cast statistical outcomes using `bool()` and `float()` before serialization. |
