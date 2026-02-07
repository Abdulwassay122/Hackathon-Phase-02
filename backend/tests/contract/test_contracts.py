import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from src.main import app
from src.database.database import get_session


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


def test_root_endpoint_contract(client):
    """Test the root endpoint contract"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)


def test_create_task_contract(client):
    """Test the POST /api/{user_id}/tasks endpoint contract"""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }

    response = client.post("/api/1/tasks", json=task_data)

    # Should return 201 Created
    assert response.status_code == 201

    # Response should match Task schema
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert isinstance(data["completed"], bool)
    assert data["user_id"] == 1
    assert "created_at" in data
    assert "updated_at" in data


def test_get_tasks_contract(client):
    """Test the GET /api/{user_id}/tasks endpoint contract"""
    # First create a task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    client.post("/api/1/tasks", json=task_data)

    response = client.get("/api/1/tasks")

    # Should return 200 OK
    assert response.status_code == 200

    # Response should be an array of tasks
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        task = data[0]
        assert "id" in task
        assert "title" in task
        assert "completed" in task
        assert "user_id" in task
        assert "created_at" in task
        assert "updated_at" in task


def test_get_specific_task_contract(client):
    """Test the GET /api/{user_id}/tasks/{id} endpoint contract"""
    # First create a task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/1/tasks", json=task_data)
    task_id = create_response.json()["id"]

    response = client.get(f"/api/1/tasks/{task_id}")

    # Should return 200 OK
    assert response.status_code == 200

    # Response should match Task schema
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"
    assert "created_at" in data
    assert "updated_at" in data


def test_update_task_contract(client):
    """Test the PUT /api/{user_id}/tasks/{id} endpoint contract"""
    # First create a task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/1/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Update the task
    update_data = {
        "title": "Updated Task",
        "description": "Updated Description",
        "completed": True
    }
    response = client.put(f"/api/1/tasks/{task_id}", json=update_data)

    # Should return 200 OK
    assert response.status_code == 200

    # Response should match Task schema
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Task"
    assert data["completed"] is True


def test_delete_task_contract(client):
    """Test the DELETE /api/{user_id}/tasks/{id} endpoint contract"""
    # First create a task
    task_data = {
        "title": "Test Task to Delete",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/1/tasks", json=task_data)
    task_id = create_response.json()["id"]

    response = client.delete(f"/api/1/tasks/{task_id}")

    # Should return 204 No Content
    assert response.status_code == 204


def test_mark_task_complete_contract(client):
    """Test the PATCH /api/{user_id}/tasks/{id}/complete endpoint contract"""
    # First create a task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/1/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Mark as complete
    complete_data = {"completed": True}
    response = client.patch(f"/api/1/tasks/{task_id}/complete", json=complete_data)

    # Should return 200 OK
    assert response.status_code == 200

    # Response should match Task schema with updated completion status
    data = response.json()
    assert data["id"] == task_id
    assert data["completed"] is True


def test_error_responses_contract(client):
    """Test error response contracts"""
    # Test 404 for non-existent task
    response = client.get("/api/1/tasks/999999")
    assert response.status_code == 404

    # Test 400 for invalid task creation data
    invalid_task_data = {
        "title": "",  # Empty title should be invalid
        "user_id": 1
    }
    response = client.post("/api/1/tasks", json=invalid_task_data)
    assert response.status_code in [400, 422]  # Could be validation error