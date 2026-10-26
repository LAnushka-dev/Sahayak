import os
import json
import numpy as np
from typing import List, Dict, Tuple
from rag.embeddings import MultilingualEmbeddings

class FAISSVectorStore:
    """
    Vector Store interface wrapping FAISS (IndexFlatIP for cosine similarity)
    with seamless numpy fallback for instant zero-dependency execution.
    """
    def __init__(self, embeddings: MultilingualEmbeddings, index_path: str = "rag/faiss_index"):
        self.embeddings = embeddings
        self.index_path = index_path
        self.documents: List[str] = []
        self.metadatas: List[Dict] = []
        self.vectors: np.ndarray = np.empty((0, self.embeddings.dimension), dtype=np.float32)
        self.has_faiss = False
        self.faiss_index = None

        try:
            import faiss
            self.has_faiss = True
        except ImportError:
            self.has_faiss = False

    def add_texts(self, texts: List[str], metadatas: List[Dict] = None):
        if not texts:
            return

        new_vectors = np.array(self.embeddings.embed_documents(texts), dtype=np.float32)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(new_vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        new_vectors = new_vectors / norms

        if self.vectors.shape[0] == 0:
            self.vectors = new_vectors
        else:
            self.vectors = np.vstack([self.vectors, new_vectors])

        self.documents.extend(texts)
        if metadatas:
            self.metadatas.extend(metadatas)
        else:
            self.metadatas.extend([{"source": "local_ingest"} for _ in texts])

        if self.has_faiss:
            import faiss
            self.faiss_index = faiss.IndexFlatIP(self.embeddings.dimension)
            self.faiss_index.add(self.vectors)

    def similarity_search(self, query: str, top_k: int = 4) -> List[Tuple[str, float, Dict]]:
        if len(self.documents) == 0:
            return []

        q_vec = np.array(self.embeddings.embed_query(query), dtype=np.float32)
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec = q_vec / norm
        q_vec = q_vec.reshape(1, -1)

        if self.has_faiss and self.faiss_index is not None:
            distances, indices = self.faiss_index.search(q_vec, min(top_k, len(self.documents)))
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx != -1 and idx < len(self.documents):
                    results.append((self.documents[idx], float(dist), self.metadatas[idx]))
            return results
        else:
            # High-performance NumPy Cosine Matrix Multiplication
            similarities = np.dot(self.vectors, q_vec.T).flatten()
            top_indices = np.argsort(similarities)[::-1][:top_k]
            results = []
            for idx in top_indices:
                results.append((self.documents[idx], float(similarities[idx]), self.metadatas[idx]))
            return results

    def save_local(self, directory: str = "rag/faiss_index"):
        os.makedirs(directory, exist_ok=True)
        np.save(os.path.join(directory, "vectors.npy"), self.vectors)
        with open(os.path.join(directory, "store.json"), "w", encoding="utf-8") as f:
            json.dump({"documents": self.documents, "metadatas": self.metadatas}, f, ensure_ascii=False)

    def load_local(self, directory: str = "rag/faiss_index") -> bool:
        v_file = os.path.join(directory, "vectors.npy")
        s_file = os.path.join(directory, "store.json")
        if os.path.exists(v_file) and os.path.exists(s_file):
            self.vectors = np.load(v_file)
            with open(s_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.documents = data.get("documents", [])
                self.metadatas = data.get("metadatas", [])
            if self.has_faiss:
                import faiss
                self.faiss_index = faiss.IndexFlatIP(self.embeddings.dimension)
                if len(self.vectors) > 0:
                    self.faiss_index.add(self.vectors)
            return True
        return False
