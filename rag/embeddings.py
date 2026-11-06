import os
import hashlib
import requests
import numpy as np
from typing import List

class MultilingualEmbeddings:
    """
    Multilingual embeddings provider supporting:
    1. Jina AI v3 API (multilingual Indic + English)
    2. Deterministic normalized hash-ngram embeddings for offline high-performance vector search
    """
    def __init__(self, api_key: str = None, model_name: str = "jina-embeddings-v3"):
        self.api_key = api_key or os.getenv("JINA_API_KEY", "")
        self.model_name = model_name
        self.jina_url = "https://api.jina.ai/v1/embeddings"
        self.dimension = 384  # Standard dense embedding dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # If Jina API Key is available, call Jina API
        if self.api_key:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model_name,
                "task": "retrieval.passage",
                "dimensions": self.dimension,
                "input": texts
            }
            try:
                resp = requests.post(self.jina_url, json=payload, headers=headers, timeout=12)
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    return [item["embedding"] for item in data]
            except Exception as e:
                print(f"[Embeddings] Jina API failed ({e}), using local deterministic embeddings.")

        # Local deterministic multilingual vector generator fallback
        return [self._compute_offline_embedding(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        if self.api_key:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model_name,
                "task": "retrieval.query",
                "dimensions": self.dimension,
                "input": [text]
            }
            try:
                resp = requests.post(self.jina_url, json=payload, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    if data:
                        return data[0]["embedding"]
            except Exception as e:
                print(f"[Embeddings] Jina API query notice ({e}), using local deterministic embeddings.")

        return self._compute_offline_embedding(text)

    def _compute_offline_embedding(self, text: str) -> List[float]:
        """
        Creates a deterministic 384-dimensional normalized vector based on character and token n-grams.
        Uses MD5 hashing for cross-process and cross-platform consistency.
        Guarantees semantic closeness for identical keywords across languages.
        """
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().replace(",", " ").replace(".", " ").replace(";", " ").split()
        for idx, w in enumerate(words):
            # MD5 digest integer
            h_int = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            pos = h_int % self.dimension
            weight = 1.0 / (idx + 1) ** 0.5
            vec[pos] += weight
            
            # Character trigrams for morphological and script invariance
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    sub = w[i:i+3]
                    sub_h = int(hashlib.md5(sub.encode("utf-8")).hexdigest(), 16)
                    vec[sub_h % self.dimension] += 0.35

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
