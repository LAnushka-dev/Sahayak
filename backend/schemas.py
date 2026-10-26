from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str

class ChatRequest(BaseModel):
    query: str
    ocr_extracted_text: Optional[str] = None
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    intent: str
    detected_language: str
    recommended_forum: str
    citations: List[str]
    draft_petition: str
    is_grounded: bool
    final_response: str
    agent_trace: List[str]

class AutomationDispatchRequest(BaseModel):
    case_id: Optional[int] = None
    recipient_email: str
    complainant_name: str
    draft_petition: str
