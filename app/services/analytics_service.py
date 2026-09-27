from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from app.models.service_request import ServiceRequest
from app.models.user import User
from app.models.request_history import RequestHistory
from app.services.sla_service import SLAService

class AnalyticsService:
    
    # ==================== SUMMARY ====================
    
    @staticmethod
    def get_summary(db: Session) -> dict:
        """Get overall analytics summary"""
        total = db.query(func.count(ServiceRequest.id)).scalar() or 0
        
        open_requests = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.status.in_(["OPEN", "ASSIGNED", "IN_PROGRESS", "ON_HOLD"])
        ).scalar() or 0
        
        in_progress = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.status == "IN_PROGRESS"
        ).scalar() or 0
        
        resolved = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.status.in_(["RESOLVED", "CLOSED"])
        ).scalar() or 0
        
        closed = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.status == "CLOSED"
        ).scalar() or 0
        
        critical = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.priority == "CRITICAL"
        ).scalar() or 0
        
        # SLA breached
        breached = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.sla_deadline.isnot(None),
            ServiceRequest.sla_deadline < datetime.now(),
            ServiceRequest.status.notin_(["RESOLVED", "CLOSED"])
        ).scalar() or 0
        
        # Average resolution time
        avg_time = db.query(func.avg(
            func.extract('epoch', ServiceRequest.resolved_at - ServiceRequest.created_at) / 3600
        )).filter(ServiceRequest.resolved_at.isnot(None)).scalar()
        
        return {
            "total_requests": total,
            "open_requests": open_requests,
            "in_progress": in_progress,
            "resolved_requests": resolved,
            "closed_requests": closed,
            "critical_requests": critical,
            "slas_breached": breached,
            "average_resolution_time": round(avg_time or 0, 2)
        }
    
    # ==================== STATUS DISTRIBUTION ====================
    
    @staticmethod
    def get_status_distribution(db: Session) -> list:
        """Get request distribution by status"""
        results = db.query(
            ServiceRequest.status, 
            func.count(ServiceRequest.id).label("count")
        ).group_by(ServiceRequest.status).all()
        return [{"status": r[0], "count": r[1]} for r in results]
    
    # ==================== PRIORITY DISTRIBUTION ====================
    
    @staticmethod
    def get_priority_distribution(db: Session) -> list:
        """Get request distribution by priority"""
        results = db.query(
            ServiceRequest.priority, 
            func.count(ServiceRequest.id).label("count")
        ).group_by(ServiceRequest.priority).all()
        return [{"priority": r[0], "count": r[1]} for r in results]
    
    # ==================== DEPARTMENT ANALYTICS ====================
    
    @staticmethod
    def get_department_stats(db: Session, department: str) -> dict:
        """Get analytics for specific department"""
        total = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.department == department
        ).scalar() or 0
        
        open_count = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.department == department,
            ServiceRequest.status.in_(["OPEN", "ASSIGNED", "IN_PROGRESS", "ON_HOLD"])
        ).scalar() or 0
        
        resolved = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.department == department,
            ServiceRequest.status.in_(["RESOLVED", "CLOSED"])
        ).scalar() or 0
        
        avg_time = db.query(func.avg(
            func.extract('epoch', ServiceRequest.resolved_at - ServiceRequest.created_at) / 3600
        )).filter(
            ServiceRequest.department == department,
            ServiceRequest.resolved_at.isnot(None)
        ).scalar()
        
        return {
            "department": department,
            "total": total,
            "open": open_count,
            "resolved": resolved,
            "average_resolution_time": round(avg_time or 0, 2)
        }
    
    @staticmethod
    def get_all_department_stats(db: Session) -> list:
        """Get analytics for all departments"""
        departments = db.query(ServiceRequest.department).distinct().all()
        results = []
        for dept in departments:
            result = AnalyticsService.get_department_stats(db, dept[0])
            results.append(result)
        return results
    
    # ==================== AGENT PERFORMANCE ====================
    
    @staticmethod
    def get_agent_performance(db: Session, agent_id: int = None, period: str = "week"):
        """Get agent performance metrics"""
        # Date filter
        now = datetime.now()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:
            start_date = datetime(2000, 1, 1)
        
        query = db.query(
            User.id,
            User.name,
            func.count(ServiceRequest.id).label("total_assigned"),
            func.sum(
                func.case(
                    (ServiceRequest.status.in_(["RESOLVED", "CLOSED"]), 1),
                    else_=0
                )
            ).label("resolved")
        ).join(
            ServiceRequest, 
            ServiceRequest.assigned_to == User.id,
            isouter=True
        ).filter(
            User.role == "SUPPORT_AGENT",
            User.status == "ACTIVE"
        )
        
        if agent_id:
            query = query.filter(User.id == agent_id)
        
        if period != "all":
            query = query.filter(ServiceRequest.created_at >= start_date)
        
        results = query.group_by(User.id, User.name).all()
        
        agent_data = []
        for row in results:
            total = row.total_assigned or 0
            resolved = row.resolved or 0
            resolution_rate = (resolved / total * 100) if total > 0 else 0
            
            # Average resolution time for this agent
            avg_time = db.query(func.avg(
                func.extract('epoch', ServiceRequest.resolved_at - ServiceRequest.created_at) / 3600
            )).filter(
                ServiceRequest.assigned_to == row.id,
                ServiceRequest.resolved_at.isnot(None)
            ).scalar()
            
            agent_data.append({
                "agent_id": row.id,
                "agent_name": row.name,
                "total_assigned": total,
                "resolved": resolved,
                "resolution_rate": round(resolution_rate, 2),
                "avg_resolution_time": round(avg_time or 0, 2)
            })
        
        return agent_data
    
    # ==================== SLA ANALYTICS ====================
    
    @staticmethod
    def get_sla_analytics(db: Session) -> dict:
        """Get SLA compliance analytics"""
        total_sla = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.sla_deadline.isnot(None)
        ).scalar() or 0
        
        # On track
        on_track = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.sla_deadline.isnot(None),
            ServiceRequest.sla_deadline > datetime.now(),
            ServiceRequest.status.notin_(["RESOLVED", "CLOSED"])
        ).scalar() or 0
        
        # At risk (80%+ of SLA time consumed)
        at_risk = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.sla_deadline.isnot(None),
            ServiceRequest.sla_deadline.between(
                datetime.now(),
                datetime.now() + timedelta(hours=2)
            ),
            ServiceRequest.status.notin_(["RESOLVED", "CLOSED"])
        ).scalar() or 0
        
        # Breached
        breached = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.sla_deadline.isnot(None),
            ServiceRequest.sla_deadline < datetime.now(),
            ServiceRequest.status.notin_(["RESOLVED", "CLOSED"])
        ).scalar() or 0
        
        # Resolved within SLA
        resolved_within = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.sla_deadline.isnot(None),
            ServiceRequest.resolved_at.isnot(None),
            ServiceRequest.resolved_at <= ServiceRequest.sla_deadline
        ).scalar() or 0
        
        total_resolved = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.resolved_at.isnot(None)
        ).scalar() or 0
        
        compliance_rate = (resolved_within / total_resolved * 100) if total_resolved > 0 else 0
        
        return {
            "total_sla": total_sla,
            "on_track": on_track,
            "at_risk": at_risk,
            "breached": breached,
            "resolved_within_sla": resolved_within,
            "compliance_rate": round(compliance_rate, 2)
        }
    
    # ==================== CATEGORY ANALYTICS ====================
    
    @staticmethod
    def get_category_analytics(db: Session) -> list:
        """Get analytics by category"""
        results = db.query(
            ServiceRequest.category,
            func.count(ServiceRequest.id).label("total"),
            func.sum(
                func.case(
                    (ServiceRequest.status.in_(["RESOLVED", "CLOSED"]), 1),
                    else_=0
                )
            ).label("resolved")
        ).group_by(ServiceRequest.category).all()
        
        return [
            {
                "category": r[0],
                "total": r[1],
                "resolved": r[2] or 0,
                "resolution_rate": round((r[2] or 0) / r[1] * 100, 2) if r[1] > 0 else 0
            }
            for r in results
        ]
    
    # ==================== TRENDS ====================
    
    @staticmethod
    def get_trends(db: Session, days: int = 7) -> list:
        """Get request trends over time"""
        results = []
        for i in range(days - 1, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())
            
            count = db.query(func.count(ServiceRequest.id)).filter(
                ServiceRequest.created_at.between(start, end)
            ).scalar() or 0
            
            results.append({
                "date": date.strftime("%Y-%m-%d"),
                "count": count
            })
        
        return results
    
    # ==================== WORKLOAD ====================
    
    @staticmethod
    def get_workload(db: Session) -> list:
        """Get current agent workload"""
        agents = db.query(User).filter(
            User.role == "SUPPORT_AGENT",
            User.status == "ACTIVE"
        ).all()
        
        workload = []
        for agent in agents:
            assigned = db.query(func.count(ServiceRequest.id)).filter(
                ServiceRequest.assigned_to == agent.id,
                ServiceRequest.status.in_(["OPEN", "ASSIGNED", "IN_PROGRESS", "ON_HOLD"])
            ).scalar() or 0
            
            workload.append({
                "agent_id": agent.id,
                "agent_name": agent.name,
                "assigned_count": assigned
            })
        
        return sorted(workload, key=lambda x: x["assigned_count"])
    
    # ==================== CUSTOM DATE RANGE ====================
    
    @staticmethod
    def get_custom_analytics(db: Session, start_date: str, end_date: str) -> dict:
        """Get analytics for custom date range"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        
        total = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.created_at.between(start, end)
        ).scalar() or 0
        
        resolved = db.query(func.count(ServiceRequest.id)).filter(
            ServiceRequest.created_at.between(start, end),
            ServiceRequest.status.in_(["RESOLVED", "CLOSED"])
        ).scalar() or 0
        
        avg_time = db.query(func.avg(
            func.extract('epoch', ServiceRequest.resolved_at - ServiceRequest.created_at) / 3600
        )).filter(
            ServiceRequest.created_at.between(start, end),
            ServiceRequest.resolved_at.isnot(None)
        ).scalar()
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_requests": total,
            "resolved_requests": resolved,
            "average_resolution_time": round(avg_time or 0, 2)
        }
    
    # ==================== EXPORT REPORT ====================
    
    @staticmethod
    def export_report(db: Session, format: str = "json"):
        """Export analytics report"""
        summary = AnalyticsService.get_summary(db)
        status_dist = AnalyticsService.get_status_distribution(db)
        priority_dist = AnalyticsService.get_priority_distribution(db)
        sla = AnalyticsService.get_sla_analytics(db)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "status_distribution": status_dist,
            "priority_distribution": priority_dist,
            "sla_analytics": sla
        }
        
        return report
    
    # ==================== DASHBOARD METRICS ====================
    
    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict:
        """Get all dashboard metrics in one call"""
        return {
            "summary": AnalyticsService.get_summary(db),
            "status_distribution": AnalyticsService.get_status_distribution(db),
            "priority_distribution": AnalyticsService.get_priority_distribution(db),
            "sla_analytics": AnalyticsService.get_sla_analytics(db),
            "trends": AnalyticsService.get_trends(db, 7)
        }