from datetime import datetime, timedelta
from app.models.service_request import RequestPriority

class SLAService:
    SLA_TARGETS = {
        "CRITICAL": 4,
        "HIGH": 8,
        "MEDIUM": 24,
        "LOW": 72
    }
    
    @staticmethod
    def calculate_sla_deadline(priority: str) -> datetime:
        hours = SLAService.SLA_TARGETS.get(priority, 24)
        return datetime.now() + timedelta(hours=hours)
    
    @staticmethod
    def calculate_sla_status(request):
        if not request.sla_deadline:
            return {"sla_status": "NOT_SET", "hours_remaining": None}
        
        now = datetime.now()
        time_remaining = (request.sla_deadline - now).total_seconds() / 3600
        
        if request.status in ["RESOLVED", "CLOSED"]:
            # Check if resolved within SLA
            if request.resolved_at and request.resolved_at <= request.sla_deadline:
                return {"sla_status": "RESOLVED_ON_TIME", "hours_remaining": 0}
            return {"sla_status": "RESOLVED_LATE", "hours_remaining": 0}
        
        if time_remaining < 0:
            return {"sla_status": "BREACHED", "hours_remaining": 0}
        elif time_remaining < (SLAService.SLA_TARGETS.get(request.priority, 24) * 0.2):
            return {"sla_status": "AT_RISK", "hours_remaining": time_remaining}
        else:
            return {"sla_status": "ON_TRACK", "hours_remaining": time_remaining}
    
    @staticmethod
    def mark_sla_resolved(request_id: int):
        # Logic to mark SLA as resolved
        pass
    
    @staticmethod
    def get_sla_breached_requests(db):
        # Logic to get breached requests
        pass