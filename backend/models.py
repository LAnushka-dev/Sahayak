from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    cases = relationship("CaseHistory", back_populates="user")

class CaseHistory(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(Text, nullable=False)
    detected_intent = Column(String(80))
    detected_language = Column(String(10), default="en")
    recommended_forum = Column(String(150))
    citations = Column(Text)  # JSON or comma-separated list
    draft_petition = Column(Text)
    is_grounded = Column(Boolean, default=True)
    status = Column(String(50), default="DRAFTED")  # DRAFTED, DISPATCHED, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cases")
