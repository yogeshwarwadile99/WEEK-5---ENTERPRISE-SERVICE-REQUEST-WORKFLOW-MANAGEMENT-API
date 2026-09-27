from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime
from app.models.service_request import ServiceRequest, RequestStatus, RequestPriority
from app.models.request_history import RequestHistory
from app.middleware.error_handler import AppException

class RequestRepository:
    @staticmethod
    def get_by_id(db: Session, request_id: int) -> ServiceRequest:
        """Get request by ID"""
        request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
        if not request:
            raise AppException("REQUEST_NOT_FOUND", f"Request SR-{request_id} not found", 404)
        return request

    @staticmethod
    def get_by_ticket_number(db: Session, ticket_number: str) -> ServiceRequest:
        """Get request by ticket number"""
        request = db.query(ServiceRequest).filter(ServiceRequest.ticket_number == ticket_number).first()
        if not request:
            raise AppException("REQUEST_NOT_FOUND", f"Request {ticket_number} not found", 404)
        return request

    @staticmethod
    def create(db: Session, request_data: dict) -> ServiceRequest:
        """Create a new request"""
        request = ServiceRequest(**request_data)
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def get_all(db: Session, filters: dict = None):
        """Get all requests with filters"""
        query = db.query(ServiceRequest)

        if filters:
            if filters.get("status"):
                query = query.filter(ServiceRequest.status == filters["status"])
            if filters.get("priority"):
                query = query.filter(ServiceRequest.priority == filters["priority"])
            if filters.get("category"):
                query = query.filter(ServiceRequest.category == filters["category"])
            if filters.get("department"):
                query = query.filter(ServiceRequest.department == filters["department"])
            if filters.get("created_by"):
                query = query.filter(ServiceRequest.created_by == filters["created_by"])
            if filters.get("assigned_to"):
                query = query.filter(ServiceRequest.assigned_to == filters["assigned_to"])
            if filters.get("search"):
                search = filters["search"]
                query = query.filter(
                    or_(
                        ServiceRequest.title.ilike(f"%{search}%"),
                        ServiceRequest.ticket_number.ilike(f"%{search}%"),
                        ServiceRequest.description.ilike(f"%{search}%")
                    )
                )

        # Sorting
        sort_by = filters.get("sort_by", "created_at")
        sort_order = filters.get("sort_order", "desc")
        if sort_order == "desc":
            query = query.order_by(getattr(ServiceRequest, sort_by).desc())
        else:
            query = query.order_by(getattr(ServiceRequest, sort_by).asc())

        # Pagination
        page = filters.get("page", 1)
        limit = filters.get("limit", 10)
        offset = (page - 1) * limit

        total = query.count()
        data = query.offset(offset).limit(limit).all()

        return {
            "total": total,
            "data": data,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    @staticmethod
    def get_by_user(db: Session, user_id: int, filters: dict = None):
        """Get requests created by a user"""
        filters = filters or {}
        filters["created_by"] = user_id
        return RequestRepository.get_all(db, filters)

    @staticmethod
    def get_by_agent(db: Session, agent_id: int, filters: dict = None):
        """Get requests assigned to an agent"""
        filters = filters or {}
        filters["assigned_to"] = agent_id
        return RequestRepository.get_all(db, filters)

    @staticmethod
    def get_by_department(db: Session, department: str, filters: dict = None):
        """Get requests by department"""
        filters = filters or {}
        filters["department"] = department
        return RequestRepository.get_all(db, filters)

    @staticmethod
    def update(db: Session, request_id: int, update_data: dict) -> ServiceRequest:
        """Update request"""
        request = RequestRepository.get_by_id(db, request_id)
        for key, value in update_data.items():
            if value is not None:
                setattr(request, key, value)
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def delete(db: Session, request_id: int) -> bool:
        """Delete request"""
        request = RequestRepository.get_by_id(db, request_id)
        db.delete(request)
        db.commit()
        return True

    @staticmethod
    def get_status_counts(db: Session) -> dict:
        """Get count of requests by status"""
        results = db.query(ServiceRequest.status, func.count(ServiceRequest.id)).group_by(
            ServiceRequest.status
        ).all()
        return {r[0]: r[1] for r in results}

    @staticmethod
    def get_priority_counts(db: Session) -> dict:
        """Get count of requests by priority"""
        results = db.query(ServiceRequest.priority, func.count(ServiceRequest.id)).group_by(
            ServiceRequest.priority
        ).all()
        return {r[0]: r[1] for r in results}

    @staticmethod
    def get_department_counts(db: Session) -> dict:
        """Get count of requests by department"""
        results = db.query(ServiceRequest.department, func.count(ServiceRequest.id)).group_by(
            ServiceRequest.department
        ).all()
        return {r[0]: r[1] for r in results}

    @staticmethod
    def get_resolved_count(db: Session) -> int:
        """Get count of resolved requests"""
        return db.query(ServiceRequest).filter(
            ServiceRequest.status.in_(["RESOLVED", "CLOSED"])
        ).count()

    @staticmethod
    def get_open_count(db: Session) -> int:
        """Get count of open requests"""
        return db.query(ServiceRequest).filter(
            ServiceRequest.status.in_(["OPEN", "ASSIGNED", "IN_PROGRESS", "ON_HOLD"])
        ).count()

    @staticmethod
    def get_average_resolution_time(db: Session) -> float:
        """Get average resolution time in hours"""
        result = db.query(func.avg(
            func.extract('epoch', ServiceRequest.resolved_at - ServiceRequest.created_at) / 3600
        )).filter(ServiceRequest.resolved_at.isnot(None)).scalar()
        return round(result or 0, 2)

    @staticmethod
    def get_breached_sla_count(db: Session) -> int:
        """Get count of SLA breached requests"""
        return db.query(ServiceRequest).filter(
            and_(
                ServiceRequest.sla_deadline.isnot(None),
                ServiceRequest.sla_deadline < datetime.now(),
                ServiceRequest.status.notin_(["RESOLVED", "CLOSED"])
            )
        ).count()

    @staticmethod
    def get_by_category(db: Session, category: str):
        """Get requests by category"""
        return db.query(ServiceRequest).filter(ServiceRequest.category == category).all()

    @staticmethod
    def get_recent_requests(db: Session, limit: int = 10):
        """Get recent requests"""
        return db.query(ServiceRequest).order_by(
            ServiceRequest.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_history(db: Session, request_id: int):
        """Get request history"""
        return db.query(RequestHistory).filter(
            RequestHistory.request_id == request_id
        ).order_by(RequestHistory.timestamp).all()

    @staticmethod
    def add_history(db: Session, history_data: dict):
        """Add request history entry"""
        history = RequestHistory(**history_data)
        db.add(history)
        db.commit()
        db.refresh(history)
        return history