# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from .db import Base

class QueryRecord(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True, index=True)
    court = Column(String, index=True)            # e.g., "Bombay High Court"
    case_type = Column(String, index=True)
    case_number = Column(String, index=True)
    case_year = Column(String, index=True)
    raw_response = Column(Text)                   # store raw HTML/JSON (truncated if huge)
    parsed = Column(JSON)                         # parsed fields (parties, dates, status, pdf_links)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
