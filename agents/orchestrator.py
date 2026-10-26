import os
from typing import Dict, Any, Optional
from agents.state import AgentState
from agents.router import router_node
from agents.retriever import retriever_node
from agents.eligibility import eligibility_node
from agents.drafter import drafter_node
from agents.critic import critic_node

class SahayakMultiAgentOrchestrator:
    """
    Multi-Agent Graph Orchestrator for Sahayak.
    Runs Router -> Retriever -> Eligibility -> Drafter -> Critic (Reflection Loop).
    """
    def __init__(self):
        self.max_retries = 2

    def invoke(self, initial_state: AgentState) -> AgentState:
        state = dict(initial_state)
        state.setdefault("agent_trace", [])
        state.setdefault("retry_count", 0)

        # 1. Router Node
        r_out = router_node(state)
        state.update(r_out)

        # 2. Retriever Node
        ret_out = retriever_node(state)
        state.update(ret_out)

        # 3. Eligibility Node
        el_out = eligibility_node(state)
        state.update(el_out)

        # Reflection loop between Drafter and Critic
        while state["retry_count"] <= self.max_retries:
            # 4. Drafter Node
            d_out = drafter_node(state)
            state.update(d_out)

            # 5. Critic Node
            c_out = critic_node(state)
            state.update(c_out)

            # Conditional routing edge evaluation
            if state["is_grounded"]:
                break
            else:
                state["agent_trace"].append(f"[LangGraph Cycle] Critic triggered loop back to Retriever (Retry: {state['retry_count']})")
                # Loop back to retrieve broader context
                ret_out = retriever_node(state)
                state.update(ret_out)

        return state

# Global orchestrator instance
orchestrator = SahayakMultiAgentOrchestrator()

def run_sahayak(query: str, ocr_extracted_text: Optional[str] = None, user_id: str = "anon", session_id: str = "default_session", preferred_language: Optional[str] = None) -> Dict[str, Any]:
    initial_state: AgentState = {
        "user_id": user_id,
        "session_id": session_id,
        "query": query,
        "detected_language": preferred_language or "en",
        "intent": "UNKNOWN",
        "ocr_extracted_text": ocr_extracted_text,
        "retrieved_documents": [],
        "graph_knowledge": [],
        "eligibility_status": None,
        "draft_petition": None,
        "citations": [],
        "is_grounded": False,
        "critic_feedback": None,
        "retry_count": 0,
        "final_response": None,
        "agent_trace": []
    }
    return orchestrator.invoke(initial_state)

# Backwards compatibility alias
run_justice_ai = run_sahayak
