"""
RAG Chunking Pipeline
Splits loaded documents into semantic chunks with full metadata attachment.
"""

from typing import List, Dict, Any

class MetadataChunker:
    def __init__(self, chunk_size: int = 400, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = doc.get("text", "")
        words = text.split()
        if not words:
            return []

        chunks = []
        start = 0
        chunk_idx = 0

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            
            chunks.append({
                "chunk_id": f"{doc['id']}_c{chunk_idx:02d}",
                "doc_id": doc["id"],
                "text": chunk_text,
                "persona": doc.get("persona"),
                "type": doc.get("type"),
                "project": doc.get("project"),
                "skills": doc.get("skills", []),
                "date": doc.get("date"),
                "client_industry": doc.get("client_industry"),
                "outcome": doc.get("outcome"),
                "source": doc.get("source")
            })
            chunk_idx += 1
            if end == len(words):
                break
            start += (self.chunk_size - self.overlap)

        return chunks

    def chunk_all(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_chunks = []
        for d in docs:
            all_chunks.extend(self.chunk_document(d))
        return all_chunks
