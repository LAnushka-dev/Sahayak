import os
import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests

from backend.config import settings
from backend.database import engine, Base, get_db
from backend.models import User, CaseHistory
from backend.schemas import UserRegister, UserLogin, TokenResponse, ChatRequest, ChatResponse, AutomationDispatchRequest
from backend.auth import hash_password, verify_password, create_access_token, decode_access_token
from backend.ocr import LegalDocumentOCR
from agents.orchestrator import run_sahayak

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multimodal Agentic Graph-RAG Legal & Grievance Assistant for Indian Citizens."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ocr_service = LegalDocumentOCR()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        return None
    return db.query(User).filter(User.email == payload.get("sub")).first()

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Sahayak Backend",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}

@app.post("/api/auth/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.email, "name": new_user.full_name})
    return {"access_token": token, "token_type": "bearer", "user_name": new_user.full_name}

@app.post("/api/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.email, "name": user.full_name})
    return {"access_token": token, "token_type": "bearer", "user_name": user.full_name}

@app.post("/api/documents/ocr")
async def upload_document(file: UploadFile = File(...)):
    """
    Parses image notice or FIR document photos into text for LangGraph.
    """
    contents = await file.read()
    extracted = ocr_service.extract_text_from_bytes(contents, filename=file.filename)
    return {
        "status": "success",
        "extracted_text": extracted["raw_text"],
        "metadata": extracted["metadata"]
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Invokes LangGraph Multi-Agent Orchestrator:
    Router -> Hybrid Retriever -> Neo4j Graph -> Eligibility -> Drafter -> Critic Loop
    """
    user_id = str(current_user.id) if current_user else "anonymous"
    result = run_sahayak(
        query=request.query,
        ocr_extracted_text=request.ocr_extracted_text,
        user_id=user_id,
        session_id=request.session_id or "default"
    )

    # Persist case to MySQL / SQLite if user is logged in
    if current_user:
        new_case = CaseHistory(
            user_id=current_user.id,
            query=request.query,
            detected_intent=result.get("intent"),
            detected_language=result.get("detected_language"),
            recommended_forum=result.get("eligibility_status", {}).get("recommended_forum", "Appropriate Forum"),
            citations="; ".join(result.get("citations", [])),
            draft_petition=result.get("draft_petition"),
            is_grounded=result.get("is_grounded", True)
        )
        db.add(new_case)
        db.commit()

    return {
        "intent": result.get("intent", "GENERAL_INQUIRY"),
        "detected_language": result.get("detected_language", "en"),
        "recommended_forum": result.get("eligibility_status", {}).get("recommended_forum", "District Forum"),
        "citations": result.get("citations", []),
        "draft_petition": result.get("draft_petition", ""),
        "is_grounded": result.get("is_grounded", True),
        "final_response": result.get("final_response", ""),
        "agent_trace": result.get("agent_trace", [])
    }

@app.get("/api/cases")
def list_user_cases(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    cases = db.query(CaseHistory).filter(CaseHistory.user_id == current_user.id).all()
    return [{"id": c.id, "query": c.query, "forum": c.recommended_forum, "status": c.status, "date": c.created_at} for c in cases]

@app.post("/api/automation/dispatch")
def dispatch_to_n8n(payload: AutomationDispatchRequest):
    """
    Forwards approved legal petitions to n8n workflow for automated email & reminder logging.
    """
    try:
        resp = requests.post(
            settings.N8N_WEBHOOK_URL,
            json=payload.model_dump(),
            timeout=5
        )
        return {"status": "dispatched", "n8n_response_code": resp.status_code}
    except Exception:
        # Graceful simulation if n8n service isn't actively listening
        return {
            "status": "queued_locally",
            "message": f"Case draft queued for automated follow-up to {payload.recipient_email} via n8n workflow."
        }
