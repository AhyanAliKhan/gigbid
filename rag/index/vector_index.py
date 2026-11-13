"""
RAG Vector Index
Dense semantic embedding index using sentence-transformers or fast scikit-learn TF-IDF dense embeddings.
"""

import numpy as np
from typing import List, Dict, Any, Tuple

class DenseVectorIndex:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = np.array([])
        self._model = None
        self._use_st = False

    def _init_model(self):
        if self._model is not None:
            return
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._model = TfidfVectorizer(max_features=1024, stop_words="english", ngram_range=(1, 2))
        self._use_st = False

    def fit_and_index(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        if not chunks:
            return
        self._init_model()
        texts = [c["text"] for c in chunks]
        
        if self._use_st:
            embs = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            self.embeddings = embs
        else:
            mat = self._model.fit_transform(texts).toarray()
            # Normalize for cosine similarity
            norms = np.linalg.norm(mat, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.embeddings = mat / norms

    def query(self, query_text: str, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if not self.chunks or len(self.embeddings) == 0:
            return []
        self._init_model()
        
        if self._use_st:
            q_emb = self._model.encode([query_text], convert_to_numpy=True, normalize_embeddings=True)[0]
        else:
            q_mat = self._model.transform([query_text]).toarray()[0]
            q_norm = np.linalg.norm(q_mat)
            q_emb = q_mat / (q_norm if q_norm > 0 else 1.0)

        # Cosine similarity
        sims = np.dot(self.embeddings, q_emb)
        top_indices = np.argsort(sims)[::-1][:k]
        
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(sims[idx])))
        return results
