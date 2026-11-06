import os
import glob
from typing import Dict, Any
from agents.state import AgentState
from rag.embeddings import MultilingualEmbeddings
from rag.vector_store import FAISSVectorStore
from rag.hybrid_retriever import HybridRAGPipeline

# Instantiate singleton resources
_embeddings = MultilingualEmbeddings()
_vector_store = FAISSVectorStore(_embeddings)

def _populate_initial_corpus():
    """Seeds the FAISS vector index from statutory texts in rag/corpus."""
    docs = []
    metas = []
    corpus_files = glob.glob("rag/corpus/*.txt")
    for fpath in corpus_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            # Split by section headers or double newlines
            sections = [s.strip() for s in content.split("\n\n") if len(s.strip()) > 30]
            for sec in sections:
                docs.append(sec)
                metas.append({"source": fname})
    if docs:
        _vector_store.add_texts(docs, metas)

_populate_initial_corpus()
_rag_pipeline = HybridRAGPipeline(_embeddings, _vector_store)

def retriever_node(state: AgentState) -> Dict[str, Any]:
    """
    Retriever Agent (Agent #2):
    Executes Hybrid RAG combining:
    1. Dense Semantic Vector Search via FAISS IndexFlatIP
    2. Sparse Lexical Search via BM25
    3. Dynamic External Legal API Search (Jina Reader & Serper)
    4. Cross-Encoder Re-ranking
    """
    query = state["query"]
    ocr_text = state.get("ocr_extracted_text")
    retry_count = state.get("retry_count", 0)
    trace = state.get("agent_trace", [])

    search_query = query
    if ocr_text:
        search_query += f" {ocr_text}"

    trace.append(f"[Retriever Agent] Executing Hybrid Search (FAISS + BM25 + Cross-Encoder) for: '{query}'")

    # If retrying after Critic reflection loop, retrieve a wider set of documents
    top_k = 4 if retry_count == 0 else 6
    retrieved_items = _rag_pipeline.retrieve(search_query, top_k=top_k, use_live_api=True)

    trace.append(f"[Retriever Agent] Successfully retrieved {len(retrieved_items)} grounded statutory chunks.")

    return {
        "retrieved_documents": retrieved_items,
        "agent_trace": trace
    }
