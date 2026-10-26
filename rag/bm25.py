import math
from typing import List, Dict

class BM25Retriever:
    """
    Lightweight, high-performance pure-Python BM25 implementation for lexical keyword matching.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0
        self.doc_lengths = []
        self.doc_term_freqs = []
        self.idf = {}
        self.documents = []

    def fit(self, documents: List[str]):
        self.documents = documents
        self.corpus_size = len(documents)
        if self.corpus_size == 0:
            return

        total_len = 0
        df = {}

        for doc in documents:
            tokens = doc.lower().replace(",", " ").replace(".", " ").split()
            self.doc_lengths.append(len(tokens))
            total_len += len(tokens)

            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_term_freqs.append(tf)

            for unique_t in tf.keys():
                df[unique_t] = df.get(unique_t, 0) + 1

        self.avg_doc_len = total_len / self.corpus_size

        for term, freq in df.items():
            # Standard Lucene/BM25 formula
            self.idf[term] = math.log(1 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self.documents:
            return []

        q_tokens = query.lower().replace(",", " ").replace(".", " ").split()
        scores = []

        for idx, tf in enumerate(self.doc_term_freqs):
            score = 0.0
            doc_len = self.doc_lengths[idx]
            len_norm = 1 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0))

            for t in q_tokens:
                if t in tf:
                    term_tf = tf[t]
                    idf_val = self.idf.get(t, 0.1)
                    denom = term_tf + self.k1 * len_norm
                    score += idf_val * ((term_tf * (self.k1 + 1)) / (denom if denom != 0 else 1.0))

            scores.append((score, idx))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for s, idx in scores[:top_k]:
            results.append({
                "document": self.documents[idx],
                "score": float(s),
                "index": idx
            })
        return results
