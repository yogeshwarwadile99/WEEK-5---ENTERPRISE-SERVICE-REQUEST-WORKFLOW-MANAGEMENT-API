import pytest

def test_register_success(client, test_user):
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "User registered successfully"
    assert data["data"]["email"] == test_user["email"]

def test_register_duplicate_email(client, test_user):
    # First registration
    client.post("/api/auth/register", json=test_user)
    # Second registration with same email
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "EMAIL_ALREADY_EXISTS"

def test_register_invalid_email(client):
    user_data = {
        "name": "Test User",
        "email": "invalid-email",
        "password": "Test@123",
        "role": "EMPLOYEE",
        "department": "IT"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 422

def test_login_success(client, test_user):
    # Register first
    client.post("/api/auth/register", json=test_user)
    # Login
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Login successful"
    assert "access_token" in data["data"]

def test_login_invalid_email(client):
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "Test@123"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "INVALID_CREDENTIALS"

def test_login_wrong_password(client, test_user):
    client.post("/api/auth/register", json=test_user)
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": "WrongPassword"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "INVALID_CREDENTIALS"

def test_get_me_success(client, test_user, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == test_user["email"]

def test_get_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_get_me_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401