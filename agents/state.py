from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """
    State contract for LangGraph multi-agent execution pipeline.
    """
    user_id: Optional[str]
    session_id: Optional[str]
    query: str
    detected_language: str
    intent: str
    ocr_extracted_text: Optional[str]
    retrieved_documents: List[Dict[str, Any]]
    graph_knowledge: List[Dict[str, Any]]
    eligibility_status: Optional[Dict[str, Any]]
    draft_petition: Optional[str]
    citations: List[str]
    is_grounded: bool
    critic_feedback: Optional[str]
    retry_count: int
    final_response: Optional[str]
    agent_trace: List[str]
