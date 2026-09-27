from pydantic import BaseModel
from typing import List, Dict, Any

class AnalyticsSummary(BaseModel):
    total_requests: int
    open_requests: int
    in_progress: int
    resolved_requests: int
    closed_requests: int
    critical_requests: int
    slas_breached: int
    average_resolution_time: float

class AnalyticsStatus(BaseModel):
    status: str
    count: int

class AnalyticsPriority(BaseModel):
    priority: str
    count: int

class AnalyticsDepartment(BaseModel):
    department: str
    total: int
    open: int
    resolved: int

class AnalyticsAgentPerformance(BaseModel):
    agent_id: int
    agent_name: str
    total_assigned: int
    resolved: int
    resolution_rate: float
    avg_resolution_time: float

class AnalyticsSLA(BaseModel):
    total_sla: int
    on_track: int
    at_risk: int
    breached: int
    compliance_rate: float