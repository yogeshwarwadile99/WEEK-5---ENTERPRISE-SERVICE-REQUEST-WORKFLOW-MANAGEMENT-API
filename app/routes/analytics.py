from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.middleware.auth import require_roles
from app.models.user import User
from app.schemas.analytics import (
    AnalyticsSummary,
    AnalyticsStatus,
    AnalyticsPriority,
    AnalyticsDepartment,
    AnalyticsAgentPerformance,
    AnalyticsSLA
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# ==================== SUMMARY ANALYTICS ====================

@router.get("/summary")
async def get_summary(
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get overall analytics summary
    
    Returns:
        - total_requests: Total number of requests
        - open_requests: Number of open requests
        - in_progress: Number of in-progress requests
        - resolved_requests: Number of resolved requests
        - closed_requests: Number of closed requests
        - critical_requests: Number of critical priority requests
        - slas_breached: Number of SLA breached requests
        - average_resolution_time: Average time to resolve in hours
    """
    data = AnalyticsService.get_summary(db)
    return {
        "success": True,
        "data": data
    }


# ==================== STATUS DISTRIBUTION ====================

@router.get("/status")
async def get_status_distribution(
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get distribution of requests by status
    
    Returns:
        - List of {status: str, count: int}
    """
    data = AnalyticsService.get_status_distribution(db)
    return {
        "success": True,
        "data": data
    }


# ==================== PRIORITY DISTRIBUTION ====================

@router.get("/priority")
async def get_priority_distribution(
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get distribution of requests by priority
    
    Returns:
        - List of {priority: str, count: int}
    """
    data = AnalyticsService.get_priority_distribution(db)
    return {
        "success": True,
        "data": data
    }


# ==================== DEPARTMENT ANALYTICS ====================

@router.get("/department")
async def get_department_analytics(
    department: Optional[str] = None,
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get analytics by department
    
    Args:
        - department: Filter by specific department (optional)
    
    Returns:
        - List of department-wise statistics
    """
    if department:
        data = AnalyticsService.get_department_stats(db, department)
    else:
        data = AnalyticsService.get_all_department_stats(db)
    
    return {
        "success": True,
        "data": data
    }


# ==================== AGENT PERFORMANCE ====================

@router.get("/agent-performance")
async def get_agent_performance(
    agent_id: Optional[int] = None,
    period: str = Query("week", description="week, month, all"),
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get agent performance metrics
    
    Args:
        - agent_id: Specific agent ID (optional)
        - period: Time period (week, month, all)
    
    Returns:
        - Agent performance metrics
    """
    data = AnalyticsService.get_agent_performance(db, agent_id, period)
    return {
        "success": True,
        "data": data
    }


# ==================== SLA ANALYTICS ====================

@router.get("/sla")
async def get_sla_analytics(
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get SLA compliance analytics
    
    Returns:
        - total_sla: Total requests with SLA
        - on_track: Requests within SLA
        - at_risk: Requests at risk of SLA breach
        - breached: SLA breached requests
        - compliance_rate: SLA compliance percentage
    """
    data = AnalyticsService.get_sla_analytics(db)
    return {
        "success": True,
        "data": data
    }


# ==================== CATEGORY ANALYTICS ====================

@router.get("/category")
async def get_category_analytics(
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get analytics by category
    
    Returns:
        - Category-wise statistics
    """
    data = AnalyticsService.get_category_analytics(db)
    return {
        "success": True,
        "data": data
    }


# ==================== TIME SERIES ANALYTICS ====================

@router.get("/trends")
async def get_trends(
    days: int = Query(7, description="Number of days to analyze"),
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get request trends over time
    
    Args:
        - days: Number of days to analyze (default: 7)
    
    Returns:
        - Daily request counts
    """
    data = AnalyticsService.get_trends(db, days)
    return {
        "success": True,
        "data": data
    }


# ==================== WORKLOAD ANALYTICS ====================

@router.get("/workload")
async def get_workload(
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get current workload distribution among agents
    
    Returns:
        - Agent workload metrics
    """
    data = AnalyticsService.get_workload(db)
    return {
        "success": True,
        "data": data
    }


# ==================== CUSTOM DATE RANGE ====================

@router.get("/custom")
async def get_custom_analytics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get analytics for custom date range
    
    Args:
        - start_date: Start date in YYYY-MM-DD format
        - end_date: End date in YYYY-MM-DD format
    
    Returns:
        - Analytics for the specified date range
    """
    data = AnalyticsService.get_custom_analytics(db, start_date, end_date)
    return {
        "success": True,
        "data": data
    }


# ==================== EXPORT REPORT ====================

@router.get("/export")
async def export_report(
    format: str = Query("json", description="Export format (json, csv)"),
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Export analytics report
    
    Args:
        - format: Export format (json or csv)
    
    Returns:
        - Report in requested format
    """
    data = AnalyticsService.export_report(db, format)
    return {
        "success": True,
        "data": data
    }


# ==================== DASHBOARD METRICS ====================

@router.get("/dashboard")
async def get_dashboard_metrics(
    current_user: User = Depends(require_roles("MANAGER", "ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Get all dashboard metrics in one call
    
    Returns:
        - Complete dashboard metrics
    """
    data = AnalyticsService.get_dashboard_metrics(db)
    return {
        "success": True,
        "data": data
    }