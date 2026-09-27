import pytest

def test_create_request_success(client, test_user, auth_headers):
    request_data = {
        "title": "Laptop not working",
        "description": "My laptop is not turning on",
        "category": "Hardware",
        "priority": "HIGH",
        "department": "IT"
    }
    response = client.post("/api/requests", json=request_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Request created successfully"
    assert "ticket_number" in data["data"]

def test_create_request_missing_fields(client, auth_headers):
    request_data = {
        "title": "Laptop not working"
    }
    response = client.post("/api/requests", json=request_data, headers=auth_headers)
    assert response.status_code == 422

def test_create_request_unauthorized(client):
    request_data = {
        "title": "Laptop not working",
        "description": "My laptop is not turning on",
        "category": "Hardware",
        "priority": "HIGH",
        "department": "IT"
    }
    response = client.post("/api/requests", json=request_data)
    assert response.status_code == 401

def test_get_requests_success(client, test_user, auth_headers):
    # Create a request first
    request_data = {
        "title": "Test Request",
        "description": "Test Description",
        "category": "Hardware",
        "priority": "MEDIUM",
        "department": "IT"
    }
    client.post("/api/requests", json=request_data, headers=auth_headers)
    
    # Get requests
    response = client.get("/api/requests", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1

def test_get_requests_with_filter(client, test_user, auth_headers):
    # Create request
    request_data = {
        "title": "High Priority Request",
        "description": "This is high priority",
        "category": "Software",
        "priority": "HIGH",
        "department": "IT"
    }
    client.post("/api/requests", json=request_data, headers=auth_headers)
    
    # Filter by priority
    response = client.get("/api/requests?priority=HIGH", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for req in data["data"]:
        assert req["priority"] == "HIGH"

def test_get_request_by_id_success(client, test_user, auth_headers):
    # Create request
    request_data = {
        "title": "Get by ID Test",
        "description": "Test description",
        "category": "Hardware",
        "priority": "MEDIUM",
        "department": "IT"
    }
    create_response = client.post("/api/requests", json=request_data, headers=auth_headers)
    request_id = create_response.json()["data"]["id"]
    
    # Get by ID
    response = client.get(f"/api/requests/{request_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Get by ID Test"

def test_get_request_not_found(client, auth_headers):
    response = client.get("/api/requests/99999", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "REQUEST_NOT_FOUND"

def test_update_request_success(client, test_user, auth_headers):
    # Create request
    request_data = {
        "title": "Original Title",
        "description": "Original Description",
        "category": "Hardware",
        "priority": "MEDIUM",
        "department": "IT"
    }
    create_response = client.post("/api/requests", json=request_data, headers=auth_headers)
    request_id = create_response.json()["data"]["id"]
    
    # Update request
    update_data = {"title": "Updated Title"}
    response = client.put(f"/api/requests/{request_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Updated Title"

def test_assign_request_success(client, test_user, test_agent, auth_headers):
    # Create agent
    client.post("/api/auth/register", json=test_agent)
    agent_login = client.post("/api/auth/login", json={
        "email": test_agent["email"],
        "password": test_agent["password"]
    })
    agent_id = agent_login.json()["data"]["user"]["id"]
    
    # Create request
    request_data = {
        "title": "Assign Test",
        "description": "Test assignment",
        "category": "Hardware",
        "priority": "MEDIUM",
        "department": "IT"
    }
    create_response = client.post("/api/requests", json=request_data, headers=auth_headers)
    request_id = create_response.json()["data"]["id"]
    
    # Assign request
    assign_data = {"assigned_to": agent_id}
    response = client.patch(f"/api/requests/{request_id}/assign", json=assign_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["assigned_to"] == agent_id

def test_update_status_invalid_transition(client, test_user, auth_headers):
    # Create request
    request_data = {
        "title": "Status Test",
        "description": "Test status transition",
        "category": "Hardware",
        "priority": "MEDIUM",
        "department": "IT"
    }
    create_response = client.post("/api/requests", json=request_data, headers=auth_headers)
    request_id = create_response.json()["data"]["id"]
    
    # Invalid transition: OPEN -> CLOSED
    status_data = {"status": "CLOSED"}
    response = client.patch(f"/api/requests/{request_id}/status", json=status_data, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_TRANSITION"