from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.service_request import RequestCreate, RequestUpdate, RequestAssign, RequestStatusUpdate, RequestPriorityUpdate
from app.services.request_service import RequestService
from app.middleware.auth import get_current_user, require_roles
from app.models.user import User

router = APIRouter(prefix="/api/requests", tags=["Service Requests"])

@router.post("/")
async def create_request(
    request_data: RequestCreate,
    current_user: User = Depends(require_roles("EMPLOYEE", "SUPPORT_AGENT", "MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    request = RequestService.create_request(db, current_user.id, request_data)
    return {"success": True, "message": "Request created successfully", "data": request}

@router.get("/")
async def get_requests(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    filters = {"status": status, "priority": priority, "search": search, "page": page, "limit": limit}
    result = RequestService.get_requests(db, current_user, filters)
    return {"success": True, "data": result["data"], "pagination": {"total": result["total"], "page": result["page"], "limit": result["limit"]}}

@router.get("/{request_id}")
async def get_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = RequestService.get_request(db, request_id, current_user)
    return {"success": True, "data": request}

@router.patch("/{request_id}/assign")
async def assign_request(
    request_id: int,
    assign_data: RequestAssign,
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    request = RequestService.assign_request(db, request_id, current_user.id, assign_data.assigned_to)
    return {"success": True, "message": "Request assigned successfully", "data": request}

@router.patch("/{request_id}/status")
async def update_status(
    request_id: int,
    status_data: RequestStatusUpdate,
    current_user: User = Depends(require_roles("SUPPORT_AGENT", "MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    request = RequestService.update_status(db, request_id, current_user.id, status_data.status)
    return {"success": True, "message": "Status updated successfully", "data": request}

@router.patch("/{request_id}/priority")
async def update_priority(
    request_id: int,
    priority_data: RequestPriorityUpdate,
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    request = RequestService.update_priority(db, request_id, current_user.id, priority_data.priority)
    return {"success": True, "message": "Priority updated successfully", "data": request}

@router.delete("/{request_id}")
async def delete_request(
    request_id: int,
    current_user: User = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db)
):
    request = RequestService.delete_request(db, request_id, current_user.id)
    return {"success": True, "message": "Request deleted successfully", "data": request}