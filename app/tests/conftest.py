import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.services.auth_service import AuthService

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Test@123",
        "role": "EMPLOYEE",
        "department": "IT"
    }

@pytest.fixture
def test_agent():
    return {
        "name": "Agent User",
        "email": "agent@example.com",
        "password": "Agent@123",
        "role": "SUPPORT_AGENT",
        "department": "IT"
    }

@pytest.fixture
def test_manager():
    return {
        "name": "Manager User",
        "email": "manager@example.com",
        "password": "Manager@123",
        "role": "MANAGER",
        "department": "IT"
    }

@pytest.fixture
def test_admin():
    return {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "Admin@123",
        "role": "ADMIN",
        "department": "IT"
    }

@pytest.fixture
def auth_headers(client, test_user):
    # Register user
    client.post("/api/auth/register", json=test_user)
    # Login
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}