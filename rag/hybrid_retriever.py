from typing import List, Dict
from rag.embeddings import MultilingualEmbeddings
from rag.vector_store import FAISSVectorStore
from rag.bm25 import BM25Retriever
from rag.reranker import CrossEncoderReranker
from rag.api_fetcher import LiveLegalAPIFetcher

class HybridRAGPipeline:
    """
    Production Hybrid RAG pipeline:
    - Dense Multilingual Vector Search (FAISS)
    - Sparse Lexical Search (BM25)
    - Dynamic External API Search (Jina Reader & Serper API)
    - Cross-Encoder Re-ranking
    """
    def __init__(self, embeddings: MultilingualEmbeddings, vector_store: FAISSVectorStore):
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.bm25 = BM25Retriever()
        self.reranker = CrossEncoderReranker()
        self.api_fetcher = LiveLegalAPIFetcher()
        self._init_bm25()

    def _init_bm25(self):
        if self.vector_store.documents:
            self.bm25.fit(self.vector_store.documents)

    def retrieve(self, query: str, top_k: int = 4, use_live_api: bool = True) -> List[Dict]:
        candidates = []

        # 1. Dense Semantic Search
        dense_hits = self.vector_store.similarity_search(query, top_k=top_k)
        for doc, score, meta in dense_hits:
            candidates.append(doc)

        # 2. Sparse Lexical BM25 Search
        bm25_hits = self.bm25.search(query, top_k=top_k)
        for hit in bm25_hits:
            if hit["document"] not in candidates:
                candidates.append(hit["document"])

        # 3. Dynamic Live API Ingestion (Jina Reader / Serper) if query needs fresh/external coverage
        if use_live_api and len(candidates) < 2:
            live_docs = self.api_fetcher.fetch_law_by_topic(query)
            for item in live_docs:
                text_block = f"[{item['title']}] ({item['source']}): {item['content']}"
                candidates.append(text_block)

        # 4. Cross-Encoder Reranking
        reranked = self.reranker.rerank(query, candidates, top_n=top_k)
        return reranked
