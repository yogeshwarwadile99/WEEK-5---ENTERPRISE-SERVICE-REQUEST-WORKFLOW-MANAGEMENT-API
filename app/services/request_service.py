from sqlalchemy.orm import Session
from datetime import datetime
import random
from app.models.service_request import ServiceRequest, RequestStatus, RequestPriority
from app.models.request_history import RequestHistory
from app.models.user import User
from app.schemas.service_request import RequestCreate
from app.services.sla_service import SLAService
from app.middleware.error_handler import AppException

class RequestService:
    @staticmethod
    def generate_ticket_number() -> str:
        return f"SR-2026-{random.randint(10000, 99999)}"
    
    @staticmethod
    def create_request(db: Session, user_id: int, request_data: RequestCreate):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AppException("USER_NOT_FOUND", "User not found", 404)
        
        ticket_number = RequestService.generate_ticket_number()
        sla_deadline = SLAService.calculate_sla_deadline(request_data.priority)
        
        request = ServiceRequest(
            ticket_number=ticket_number,
            title=request_data.title,
            description=request_data.description,
            category=request_data.category,
            priority=request_data.priority,
            status=RequestStatus.OPEN,
            created_by=user_id,
            department=request_data.department,
            sla_deadline=sla_deadline
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        return request
    
    @staticmethod
    def get_requests(db: Session, user: User, filters: dict):
        query = db.query(ServiceRequest)
        
        if user.role == "EMPLOYEE":
            query = query.filter(ServiceRequest.created_by == user.id)
        elif user.role == "SUPPORT_AGENT":
            query = query.filter(ServiceRequest.assigned_to == user.id)
        elif user.role == "MANAGER":
            query = query.filter(ServiceRequest.department == user.department)
        
        if filters.get("status"):
            query = query.filter(ServiceRequest.status == filters["status"])
        if filters.get("priority"):
            query = query.filter(ServiceRequest.priority == filters["priority"])
        if filters.get("search"):
            query = query.filter(ServiceRequest.title.ilike(f"%{filters['search']}%"))
        
        page = int(filters.get("page", 1))
        limit = int(filters.get("limit", 10))
        offset = (page - 1) * limit
        
        total = query.count()
        requests = query.offset(offset).limit(limit).all()
        return {"total": total, "data": requests, "page": page, "limit": limit}
    
    @staticmethod
    def get_request(db: Session, request_id: int, user: User):
        request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not request:
            raise AppException("REQUEST_NOT_FOUND", "Request not found", 404)
        
        if user.role == "EMPLOYEE" and request.created_by != user.id:
            raise AppException("ACCESS_DENIED", "Access denied", 403)
        
        # Calculate SLA status
        from app.services.sla_service import SLAService
        sla_info = SLAService.calculate_sla_status(request)
        request.sla_status = sla_info.get("sla_status")
        request.hours_remaining = sla_info.get("hours_remaining")
        
        return request
    
    @staticmethod
    def update_status(db: Session, request_id: int, user_id: int, new_status: str):
        request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not request:
            raise AppException("REQUEST_NOT_FOUND", "Request not found", 404)
        
        # Define valid transitions
        valid_transitions = {
            "OPEN": ["ASSIGNED", "REJECTED"],
            "ASSIGNED": ["IN_PROGRESS", "ON_HOLD"],
            "IN_PROGRESS": ["RESOLVED", "ON_HOLD"],
            "ON_HOLD": ["IN_PROGRESS"],
            "RESOLVED": ["CLOSED"],
            "CLOSED": [],
            "REJECTED": []
        }
        
        if new_status not in valid_transitions.get(request.status, []):
            raise AppException("INVALID_TRANSITION", 
                f"Invalid status transition from {request.status} to {new_status}", 400)
        
        old_status = request.status
        request.status = new_status
        
        if new_status == "RESOLVED":
            request.resolved_at = datetime.now()
        elif new_status == "CLOSED":
            request.closed_at = datetime.now()
        
        db.commit()
        db.refresh(request)
        return request
    
    @staticmethod
    def assign_request(db: Session, request_id: int, user_id: int, assigned_to: int):
        request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not request:
            raise AppException("REQUEST_NOT_FOUND", "Request not found", 404)
        
        agent = db.query(User).filter(User.id == assigned_to).first()
        if not agent:
            raise AppException("AGENT_NOT_FOUND", "Agent not found", 404)
        
        if agent.role not in ["SUPPORT_AGENT", "ADMIN"]:
            raise AppException("INVALID_AGENT", "User is not a support agent", 400)
        
        request.assigned_to = assigned_to
        request.status = "ASSIGNED"
        db.commit()
        db.refresh(request)
        return request
