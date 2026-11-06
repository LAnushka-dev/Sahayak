import os
from typing import Dict, Any, Optional
from agents.state import AgentState
from agents.router import router_node
from agents.retriever import retriever_node
from agents.graph_reasoner import graph_reasoner_node
from agents.drafter import drafter_node
from agents.critic import critic_node

# Attempt to build and compile the genuine LangGraph StateGraph
_langgraph_available = False
_compiled_graph = None

try:
    from langgraph.graph import StateGraph, END

    def should_continue(state: AgentState) -> str:
        """Conditional routing edge for LangGraph self-correcting reflection loop."""
        if state.get("is_grounded", False):
            return "end"
        if state.get("retry_count", 0) >= 2:
            return "end"
        state["agent_trace"].append(
            f"[LangGraph Reflection Edge] Critic detected ungrounded citations -> Looping back to Retriever (Retry {state.get('retry_count')})"
        )
        return "loop_back"

    workflow = StateGraph(AgentState)
    workflow.add_node("router", router_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("graph_reasoner", graph_reasoner_node)
    workflow.add_node("drafter", drafter_node)
    workflow.add_node("critic", critic_node)

    workflow.set_entry_point("router")
    workflow.add_edge("router", "retriever")
    workflow.add_edge("retriever", "graph_reasoner")
    workflow.add_edge("graph_reasoner", "drafter")
    workflow.add_edge("drafter", "critic")

    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "loop_back": "retriever",
            "end": END
        }
    )

    _compiled_graph = workflow.compile()
    _langgraph_available = True
    print("[LangGraph] Multi-Agent StateGraph successfully constructed and compiled with 5 Agents.")

except Exception as e:
    print(f"[LangGraph Notice] Fallback orchestrator active ({e}).")
    _langgraph_available = False
    _compiled_graph = None


class SahayakMultiAgentOrchestrator:
    """
    Coordinates 5 AI agents (Router, Retriever, Graph Reasoner, Drafter, Critic)
    using LangGraph StateGraph with conditional reflection loop.
    """
    def __init__(self):
        self.max_retries = 2

    def invoke(self, initial_state: AgentState) -> AgentState:
        # If LangGraph StateGraph is compiled, run native LangGraph
        if _langgraph_available and _compiled_graph is not None:
            try:
                state_dict = dict(initial_state)
                output = _compiled_graph.invoke(state_dict)
                return output
            except Exception as e:
                initial_state.setdefault("agent_trace", []).append(
                    f"[LangGraph Execution Note] Fallback loop executed: {e}"
                )

        # Resilient fallback coordinating the 5 agents
        state = dict(initial_state)
        state.setdefault("agent_trace", [])
        state.setdefault("retry_count", 0)

        # 1. Router Agent
        state.update(router_node(state))

        # 2. Retriever Agent
        state.update(retriever_node(state))

        # 3. Graph Reasoner Agent
        state.update(graph_reasoner_node(state))

        # Self-correcting reflection loop between Drafter and Critic
        while state["retry_count"] <= self.max_retries:
            # 4. Drafter Agent
            state.update(drafter_node(state))

            # 5. Critic Agent
            state.update(critic_node(state))

            if state.get("is_grounded", False):
                break
            else:
                state["agent_trace"].append(
                    f"[LangGraph Reflection Edge] Critic detected ungrounded citations -> Looping back to Retriever (Retry {state['retry_count']})"
                )
                state.update(retriever_node(state))
                state.update(graph_reasoner_node(state))

        return state

# Global orchestrator instance
orchestrator = SahayakMultiAgentOrchestrator()

def run_sahayak(
    query: str,
    ocr_extracted_text: Optional[str] = None,
    user_id: str = "anon",
    session_id: str = "default_session",
    preferred_language: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entrypoint invoking the 5-Agent LangGraph system:
    Router -> Retriever -> Graph Reasoner -> Drafter -> Critic (Reflection Loop).
    """
    initial_state: AgentState = {
        "user_id": user_id,
        "session_id": session_id,
        "query": query,
        "detected_language": preferred_language or "auto",
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
