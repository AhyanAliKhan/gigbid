"""
RAG Retriever Factory & Coordinator
Initializes multi-format ingestion, chunking, indices (Vector, BM25, Graph),
and instantiates the configured RAG variant (V0 to V9).
"""

import os
from typing import List, Dict, Any, Optional
from rag.ingest.loaders import DocumentLoader
from rag.ingest.chunker import MetadataChunker
from rag.index.vector_index import DenseVectorIndex
from rag.index.bm25_index import BM25Index
from rag.index.graph_index import SkillGraphIndex

from rag.variants.v0_naive import V0NaiveRetriever
from rag.variants.v1_requirement_decomp import V1RequirementDecompRetriever
from rag.variants.v2_hybrid import V2HybridRetriever
from rag.variants.v3_cross_encoder import V3CrossEncoderRetriever
from rag.variants.v4_outcome_aware import V4OutcomeAwareRetriever
from rag.variants.v8_self_rag import V8SelfRAGRetriever
from rag.variants.v9_skill_graph import V9SkillGraphRetriever

class RAGPipeline:
    def __init__(self, persona_id: str = "alex_chen_aiml"):
        self.persona_id = persona_id
        self.loader = DocumentLoader()
        self.chunker = MetadataChunker(chunk_size=300, overlap=40)
        
        self.vector_index = DenseVectorIndex()
        self.bm25_index = BM25Index()
        self.graph_index = SkillGraphIndex()
        
        self.chunks: List[Dict[str, Any]] = []
        self._build_indices()

    def _build_indices(self):
        docs = self.loader.load_all_documents_for_persona(self.persona_id)
        self.chunks = self.chunker.chunk_all(docs)
        self.vector_index.fit_and_index(self.chunks)
        self.bm25_index.fit_and_index(self.chunks)
        self.graph_index.fit_and_index(self.chunks)

    def reindex_incremental(self, new_doc: Dict[str, Any]):
        """Incremental re-indexing when user adds work in the UI."""
        new_chunks = self.chunker.chunk_document(new_doc)
        self.chunks.extend(new_chunks)
        self.vector_index.fit_and_index(self.chunks)
        self.bm25_index.fit_and_index(self.chunks)
        self.graph_index.fit_and_index(self.chunks)

    def get_retriever(self, variant: str = "v2"):
        v = variant.lower()
        if v in ["v0", "v0_naive"]:
            return V0NaiveRetriever(self.vector_index)
        elif v in ["v1", "v1_requirement_decomp"]:
            return V1RequirementDecompRetriever(self.vector_index)
        elif v in ["v2", "v2_hybrid"]:
            return V2HybridRetriever(self.vector_index, self.bm25_index)
        elif v in ["v3", "v3_cross_encoder"]:
            v2 = V2HybridRetriever(self.vector_index, self.bm25_index)
            return V3CrossEncoderRetriever(v2)
        elif v in ["v4", "v4_outcome_aware"]:
            v2 = V2HybridRetriever(self.vector_index, self.bm25_index)
            return V4OutcomeAwareRetriever(v2)
        elif v in ["v8", "v8_self_rag"]:
            v2 = V2HybridRetriever(self.vector_index, self.bm25_index)
            return V8SelfRAGRetriever(v2)
        elif v in ["v9", "v9_skill_graph"]:
            return V9SkillGraphRetriever(self.graph_index)
        else:
            # Default to best shipped retriever (V2 Hybrid)
            return V2HybridRetriever(self.vector_index, self.bm25_index)

_PIPELINE_CACHE: Dict[str, RAGPipeline] = {}

def get_rag_pipeline(persona_id: str = "alex_chen_aiml") -> RAGPipeline:
    if persona_id not in _PIPELINE_CACHE:
        _PIPELINE_CACHE[persona_id] = RAGPipeline(persona_id)
    return _PIPELINE_CACHE[persona_id]
