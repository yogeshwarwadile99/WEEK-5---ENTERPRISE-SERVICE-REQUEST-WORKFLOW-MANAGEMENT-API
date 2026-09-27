import pytest
from app.services.sla_service import SLAService

def test_sla_deadline_calculation():
    # Critical priority - 4 hours
    deadline = SLAService.calculate_sla_deadline("CRITICAL")
    assert deadline is not None
    
    # Low priority - 72 hours
    deadline = SLAService.calculate_sla_deadline("LOW")
    assert deadline is not None

def test_sla_targets():
    assert SLAService.SLA_TARGETS["CRITICAL"] == 4
    assert SLAService.SLA_TARGETS["HIGH"] == 8
    assert SLAService.SLA_TARGETS["MEDIUM"] == 24
    assert SLAService.SLA_TARGETS["LOW"] == 72

def test_sla_status_not_set():
    from datetime import datetime
    from app.models.service_request import ServiceRequest
    
    request = ServiceRequest()
    request.sla_deadline = None
    request.status = "OPEN"
    
    result = SLAService.calculate_sla_status(request)
    assert result["sla_status"] == "NOT_SET"
    assert result["hours_remaining"] is None

def test_sla_status_on_track():
    from datetime import datetime, timedelta
    from app.models.service_request import ServiceRequest
    
    request = ServiceRequest()
    request.sla_deadline = datetime.now() + timedelta(hours=10)
    request.priority = "MEDIUM"
    request.status = "IN_PROGRESS"
    
    result = SLAService.calculate_sla_status(request)
    assert result["sla_status"] == "ON_TRACK"
    assert result["hours_remaining"] > 0

def test_sla_status_at_risk():
    from datetime import datetime, timedelta
    from app.models.service_request import ServiceRequest
    
    request = ServiceRequest()
    request.sla_deadline = datetime.now() + timedelta(hours=3)
    request.priority = "MEDIUM"
    request.status = "IN_PROGRESS"
    
    result = SLAService.calculate_sla_status(request)
    assert result["sla_status"] == "AT_RISK"

def test_sla_status_breached():
    from datetime import datetime, timedelta
    from app.models.service_request import ServiceRequest
    
    request = ServiceRequest()
    request.sla_deadline = datetime.now() - timedelta(hours=1)
    request.priority = "MEDIUM"
    request.status = "IN_PROGRESS"
    
    result = SLAService.calculate_sla_status(request)
    assert result["sla_status"] == "BREACHED"
    assert result["hours_remaining"] == 0