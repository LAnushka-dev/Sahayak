from agents.state import AgentState
from rag.embeddings import MultilingualEmbeddings
from rag.vector_store import FAISSVectorStore
from rag.hybrid_retriever import HybridRAGPipeline
from graph.neo4j_client import KnowledgeGraphClient

# Instantiate singleton resources
_embeddings = MultilingualEmbeddings()
_vector_store = FAISSVectorStore(_embeddings)

# If vector store is empty, load seed documents from corpus
def _populate_initial_corpus():
    import glob
    import os
    docs = []
    metas = []
    corpus_files = glob.glob("rag/corpus/*.txt")
    for fpath in corpus_files:
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            # Split into reasonable section chunks
            sections = [s.strip() for s in content.split("\n\n") if len(s.strip()) > 30]
            for sec in sections:
                docs.append(sec)
                metas.append({"source": fname})
    if docs:
        _vector_store.add_texts(docs, metas)

_populate_initial_corpus()
_rag_pipeline = HybridRAGPipeline(_embeddings, _vector_store)
_graph_client = KnowledgeGraphClient()

def retriever_node(state: AgentState) -> dict:
    """
    Retriever Agent: Combines Vector Store, BM25, Live APIs, and Knowledge Graph paths.
    """
    query = state["query"]
    intent = state.get("intent", "GENERAL_INQUIRY")
    trace = state.get("agent_trace", [])

    trace.append(f"[Retriever Agent] Querying Hybrid RAG (FAISS + BM25 + Jina) for: '{query}'")
    
    # 1. Hybrid Retrieval
    retrieved_items = _rag_pipeline.retrieve(query, top_k=3, use_live_api=True)

    # 2. Graph Traversal
    trace.append(f"[Retriever Agent] Performing Knowledge Graph Traversal for intent: {intent}")
    domain = "consumer" if intent == "CONSUMER_GRIEVANCE" else "rti" if intent == "RTI_QUERY" else "scheme"
    graph_results = _graph_client.query_graph_for_remedy(domain)

    trace.append(f"[Retriever Agent] Retrieved {len(retrieved_items)} legal clauses and {len(graph_results)} graph paths.")

    return {
        "retrieved_documents": retrieved_items,
        "graph_knowledge": graph_results,
        "agent_trace": trace
    }
