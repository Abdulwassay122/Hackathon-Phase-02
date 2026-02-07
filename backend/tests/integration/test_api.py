import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from src.main import app
from src.database.database import get_session
from src.models.task_model import Task


@pytest.fixture(name="session")
def session_fixture():
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
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_task(client: TestClient):
    """Test creating a new task"""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }

    response = client.post("/api/1/tasks", json=task_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert data["user_id"] == 1
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_tasks_for_user(client: TestClient):
    """Test getting all tasks for a user"""
    # Create a task first
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    client.post("/api/1/tasks", json=task_data)

    # Get all tasks for user 1
    response = client.get("/api/1/tasks")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Task"


def test_get_specific_task(client: TestClient):
    """Test getting a specific task"""
    # Create a task first
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/1/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Get the specific task
    response = client.get(f"/api/1/tasks/{task_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Test Task"
    assert data["id"] == task_id


def test_update_task(client: TestClient):
    """Test updating a task"""
    # Create a task first
    task_data = {
        "title": "Original Task",
        "description": "Original Description",
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
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated Description"
    assert data["completed"] is True


def test_delete_task(client: TestClient):
    """Test deleting a task"""
    # Create a task first
    task_data = {
        "title": "Test Task to Delete",
        "description": "Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/1/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Delete the task
    response = client.delete(f"/api/1/tasks/{task_id}")
    assert response.status_code == 204

    # Verify the task is gone
    get_response = client.get(f"/api/1/tasks/{task_id}")
    assert get_response.status_code == 404


def test_mark_task_complete(client: TestClient):
    """Test marking a task as complete"""
    # Create a task first
    task_data = {
        "title": "Test Task",
        "description": "Description",
        "completed": False,
        "user_id": 1
    }
    create_response = client.post("/api/1/tasks", json=task_data)
    task_id = create_response.json()["id"]

    # Mark the task as complete
    complete_data = {"completed": True}
    response = client.patch(f"/api/1/tasks/{task_id}/complete", json=complete_data)
    assert response.status_code == 200

    data = response.json()
    assert data["completed"] is True