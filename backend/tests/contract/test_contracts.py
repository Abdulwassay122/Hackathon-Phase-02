"""
Contract tests for API endpoints
Validates OpenAPI specification compliance with JWT authentication
"""
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from src.main import app
from src.database.database import get_session
from src.models.task_model import Task
from src.config import get_settings


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """Create a test client for the API with test database"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def valid_token():
    """Generate a valid JWT token for test user 1"""
    settings = get_settings()
    payload = {
        "sub": "1",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def valid_token_user_2():
    """Generate a valid JWT token for test user 2"""
    settings = get_settings()
    payload = {
        "sub": "2",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def auth_headers(valid_token):
    """Generate authorization headers with valid token"""
    return {"Authorization": f"Bearer {valid_token}"}


def test_root_endpoint_contract(client):
    """Test the root endpoint contract"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)


def test_create_task_contract(client, auth_headers):
    """T054: Test the POST /api/tasks endpoint contract with authentication"""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }

    response = client.post("/api/tasks", json=task_data, headers=auth_headers)

    # Should return 201 Created
    assert response.status_code == 201

    # Response should match TaskRead schema
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert isinstance(data["completed"], bool)
    assert data["completed"] is False
    assert data["user_id"] == 1
    assert "created_at" in data
    assert isinstance(data["created_at"], str)
    assert "updated_at" in data
    assert isinstance(data["updated_at"], str)


def test_get_tasks_contract(client, auth_headers):
    """T053: Test the GET /api/tasks endpoint contract with authentication"""
    # First create a task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    client.post("/api/tasks", json=task_data, headers=auth_headers)

    response = client.get("/api/tasks", headers=auth_headers)

    # Should return 200 OK
    assert response.status_code == 200

    # Response should be an array of tasks
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    task = data[0]
    assert "id" in task
    assert isinstance(task["id"], int)
    assert "title" in task
    assert isinstance(task["title"], str)
    assert "completed" in task
    assert isinstance(task["completed"], bool)
    assert "user_id" in task
    assert task["user_id"] == 1
    assert "created_at" in task
    assert "updated_at" in task


def test_get_specific_task_contract(client, auth_headers):
    """T055: Test the GET /api/tasks/{id} endpoint contract with authentication"""
    # First create a task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/tasks", json=task_data, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)

    # Should return 200 OK
    assert response.status_code == 200

    # Response should match TaskRead schema
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["user_id"] == 1
    assert "created_at" in data
    assert "updated_at" in data


def test_update_task_contract(client, auth_headers):
    """T056: Test the PUT /api/tasks/{id} endpoint contract with authentication"""
    # First create a task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/tasks", json=task_data, headers=auth_headers)
    task_id = create_response.json()["id"]

    # Update the task
    update_data = {
        "title": "Updated Task",
        "description": "Updated Description",
        "completed": True
    }
    response = client.put(f"/api/tasks/{task_id}", json=update_data, headers=auth_headers)

    # Should return 200 OK
    assert response.status_code == 200

    # Response should match TaskRead schema
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated Description"
    assert data["completed"] is True
    assert data["user_id"] == 1


def test_delete_task_contract(client, auth_headers):
    """T057: Test the DELETE /api/tasks/{id} endpoint contract with authentication"""
    # First create a task
    task_data = {
        "title": "Test Task to Delete",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/tasks", json=task_data, headers=auth_headers)
    task_id = create_response.json()["id"]

    response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)

    # Should return 204 No Content
    assert response.status_code == 204


def test_mark_task_complete_contract(client, auth_headers):
    """T058: Test the PATCH /api/tasks/{id}/complete endpoint contract with authentication"""
    # First create a task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/tasks", json=task_data, headers=auth_headers)
    task_id = create_response.json()["id"]

    # Mark as complete
    complete_data = {"completed": True}
    response = client.patch(f"/api/tasks/{task_id}/complete", json=complete_data, headers=auth_headers)

    # Should return 200 OK
    assert response.status_code == 200

    # Response should match TaskRead schema with updated completion status
    data = response.json()
    assert data["id"] == task_id
    assert data["completed"] is True
    assert data["user_id"] == 1


def test_unauthorized_response_contract(client):
    """T059: Test 401/403 Unauthorized response format"""
    # Test without token - FastAPI HTTPBearer returns 403
    response = client.get("/api/tasks")

    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)

    # Test with invalid token - returns 401
    response = client.get(
        "/api/tasks",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_forbidden_response_contract(client, valid_token, valid_token_user_2, session):
    """T060: Test 403 Forbidden response format"""
    # Create a task for user 1
    task = Task(
        title="User 1 Task",
        description="Description",
        user_id=1,
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # User 2 tries to access User 1's task
    response = client.get(
        f"/api/tasks/{task.id}",
        headers={"Authorization": f"Bearer {valid_token_user_2}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)
    assert "permission" in data["detail"].lower()


def test_not_found_response_contract(client, auth_headers):
    """Test 404 Not Found response format"""
    response = client.get("/api/tasks/999999", headers=auth_headers)

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)


def test_validation_error_response_contract(client, auth_headers):
    """Test 422 Validation Error response format"""
    # Test with empty title (should fail validation)
    invalid_task_data = {
        "title": "",
        "user_id": 1
    }
    response = client.post("/api/tasks", json=invalid_task_data, headers=auth_headers)

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
