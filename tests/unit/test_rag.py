"""
Unit tests for RAG Ingestion, Indices, Variants, and Claim Verification.
"""

import pytest
from rag.ingest.loaders import DocumentLoader
from rag.ingest.chunker import MetadataChunker
from rag.retriever import get_rag_pipeline
from rag.verify import claim_verifier

def test_document_loader_and_chunker():
    loader = DocumentLoader()
    docs = loader.load_all_documents_for_persona("alex_chen_aiml")
    assert len(docs) > 20 # CV, 20 case studies, 5 repos, 15 reviews, 150 proposals
    
    chunker = MetadataChunker(chunk_size=200, overlap=30)
    chunks = chunker.chunk_all(docs[:5])
    assert len(chunks) >= 5
    assert "persona" in chunks[0]
    assert "skills" in chunks[0]
    assert "chunk_id" in chunks[0]

def test_rag_retriever_variants():
    pipeline = get_rag_pipeline("alex_chen_aiml")
    
    # V0
    v0 = pipeline.get_retriever("v0")
    h0 = v0.retrieve("Machine Learning classification", k=3)
    assert len(h0) > 0
    assert h0[0]["variant"] == "V0_naive"

    # V2 Hybrid
    v2 = pipeline.get_retriever("v2")
    h2 = v2.retrieve("PyTorch vLLM inference", k=3)
    assert len(h2) > 0
    assert h2[0]["variant"] == "V2_hybrid_rrf"

    # V9 Skill Graph
    v9 = pipeline.get_retriever("v9")
    h9 = v9.retrieve(["PyTorch", "Python"], industry="Fintech", k=3)
    assert len(h9) > 0
    assert h9[0]["variant"] == "V9_skill_graph"

def test_claim_verification():
    evidence_pool = [{
        "chunk_id": "CS-ALEX-001_c00",
        "doc_id": "CS-ALEX-001",
        "text": "Engineered low-latency vLLM inference pipeline in PyTorch. Reduced latency by 48% and served 10,000 requests per minute.",
        "metadata": {"skills": ["Python", "PyTorch", "vLLM"], "project": "vLLM Serving"}
    }]

    # 1. Grounded proposal
    grounded_text = "Hello,\nI read your posting. In past work (CS-ALEX-001), I built a low-latency vLLM inference pipeline in PyTorch and reduced latency by 48%.\nBest regards,"
    res = claim_verifier.verify_and_ground_proposal(grounded_text, evidence_pool)
    assert res.total_claims >= 1
    assert res.unsupported_rate_after == 0.0

    # 2. Hallucinated / ungrounded proposal
    hallucinated_text = "Hello,\nI have 30 years of quantum computing experience and guarantee 100% bug free code for your bank.\nBest regards,"
    res_hal = claim_verifier.verify_and_ground_proposal(hallucinated_text, evidence_pool)
    assert res_hal.unsupported_claims > 0
    assert res_hal.unsupported_rate_before > 0.0
    assert res_hal.unsupported_rate_after == 0.0
