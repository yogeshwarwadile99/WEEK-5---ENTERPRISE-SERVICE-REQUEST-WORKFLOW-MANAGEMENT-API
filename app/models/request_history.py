from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class RequestHistory(Base):
    __tablename__ = "request_history"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=True)
    old_priority = Column(String(20), nullable=True)
    new_priority = Column(String(20), nullable=True)
    old_assigned_to = Column(Integer, nullable=True)
    new_assigned_to = Column(Integer, nullable=True)
    notes = Column(String(255), nullable=True)
    timestamp = Column(DateTime, server_default=func.now())