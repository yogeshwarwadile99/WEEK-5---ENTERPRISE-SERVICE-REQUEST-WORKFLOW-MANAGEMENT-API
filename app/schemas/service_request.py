from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RequestCreate(BaseModel):
    title: str
    description: str
    category: str
    priority: str = "MEDIUM"
    department: str

class RequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None

class RequestAssign(BaseModel):
    assigned_to: int

class RequestStatusUpdate(BaseModel):
    status: str

class RequestPriorityUpdate(BaseModel):
    priority: str

class RequestResponse(BaseModel):
    id: int
    ticket_number: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    created_by: int
    assigned_to: Optional[int]
    department: str
    sla_deadline: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    sla_status: Optional[str] = None
    hours_remaining: Optional[float] = None
    
    class Config:
        from_attributes = True