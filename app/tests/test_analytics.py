import pytest

def test_get_analytics_summary(client, test_user, test_agent, auth_headers):
    # Create user
    client.post("/api/auth/register", json=test_user)
    client.post("/api/auth/register", json=test_agent)
    
    # Create requests
    request_data1 = {
        "title": "Request 1",
        "description": "Test 1",
        "category": "Hardware",
        "priority": "HIGH",
        "department": "IT"
    }
    request_data2 = {
        "title": "Request 2",
        "description": "Test 2",
        "category": "Software",
        "priority": "MEDIUM",
        "department": "IT"
    }
    client.post("/api/requests", json=request_data1, headers=auth_headers)
    client.post("/api/requests", json=request_data2, headers=auth_headers)
    
    # Get summary
    response = client.get("/api/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total_requests"] >= 2

def test_get_status_distribution(client, test_user, auth_headers):
    response = client.get("/api/analytics/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

def test_get_priority_distribution(client, test_user, auth_headers):
    response = client.get("/api/analytics/priority", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

def test_analytics_unauthorized(client):
    response = client.get("/api/analytics/summary")
    assert response.status_code == 401

def test_analytics_employee_only(client, test_user, auth_headers):
    # Employee cannot access analytics
    response = client.get("/api/analytics/summary", headers=auth_headers)
    assert response.status_code == 403