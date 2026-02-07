"""
API Authentication Integration Tests
Tests authentication flow for task API endpoints
"""
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from src.main import app
from src.database.database import get_session
from src.models.task_model import Task
from src.config import get_settings


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override"""
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
def expired_token():
    """Generate an expired JWT token"""
    settings = get_settings()
    payload = {
        "sub": "1",
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture
def sample_tasks(session: Session):
    """Create sample tasks for testing"""
    tasks = [
        Task(title="User 1 Task 1", description="Description 1", user_id=1, completed=False),
        Task(title="User 1 Task 2", description="Description 2", user_id=1, completed=True),
        Task(title="User 2 Task 1", description="Description 3", user_id=2, completed=False),
    ]
    for task in tasks:
        session.add(task)
    session.commit()
    return tasks


class TestGetTasksAuthentication:
    """Tests for GET /api/tasks authentication"""

    def test_get_tasks_without_token(self, client: TestClient):
        """T030: Test GET /api/tasks without token returns 403"""
        response = client.get("/api/tasks")

        assert response.status_code == 403
        assert "detail" in response.json()

    def test_get_tasks_with_invalid_token(self, client: TestClient):
        """T030: Test GET /api/tasks with invalid token returns 401"""
        response = client.get(
            "/api/tasks",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_get_tasks_with_expired_token(self, client: TestClient, expired_token: str):
        """T030: Test GET /api/tasks with expired token returns 401"""
        response = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_get_tasks_with_valid_token(self, client: TestClient, valid_token: str, sample_tasks):
        """T031: Test GET /api/tasks with valid token returns user's tasks only"""
        response = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)
        assert len(tasks) == 2  # Only user 1's tasks
        assert all(task["user_id"] == 1 for task in tasks)

    def test_get_tasks_user_isolation(self, client: TestClient, valid_token_user_2: str, sample_tasks):
        """T031: Test GET /api/tasks enforces user data isolation"""
        response = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {valid_token_user_2}"}
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1  # Only user 2's task
        assert tasks[0]["user_id"] == 2


class TestPostTaskAuthentication:
    """Tests for POST /api/tasks authentication"""

    def test_post_task_without_token(self, client: TestClient):
        """T030: Test POST /api/tasks without token returns 403"""
        task_data = {
            "title": "New Task",
            "description": "Task description"
        }
        response = client.post("/api/tasks", json=task_data)

        assert response.status_code == 403
        assert "detail" in response.json()

    def test_post_task_with_invalid_token(self, client: TestClient):
        """T030: Test POST /api/tasks with invalid token returns 401"""
        task_data = {
            "title": "New Task",
            "description": "Task description"
        }
        response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_post_task_with_valid_token(self, client: TestClient, valid_token: str):
        """T032: Test POST /api/tasks with valid token creates task"""
        task_data = {
            "title": "New Task",
            "description": "Task description"
        }
        response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 201
        created_task = response.json()
        assert created_task["title"] == "New Task"
        assert created_task["description"] == "Task description"
        assert created_task["user_id"] == 1
        assert created_task["completed"] is False
        assert "id" in created_task

    def test_post_task_auto_sets_user_id(self, client: TestClient, valid_token: str):
        """T032: Test POST /api/tasks automatically sets user_id from token"""
        task_data = {
            "title": "Auto User ID Task",
            "description": "Should get user_id from token"
        }
        response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 201
        created_task = response.json()
        assert created_task["user_id"] == 1


class TestOtherEndpointsAuthentication:
    """Tests for other task endpoints authentication"""

    def test_get_task_by_id_without_token(self, client: TestClient, sample_tasks):
        """Test GET /api/tasks/{id} without token returns 403"""
        response = client.get("/api/tasks/1")

        assert response.status_code == 403

    def test_put_task_without_token(self, client: TestClient, sample_tasks):
        """Test PUT /api/tasks/{id} without token returns 403"""
        update_data = {"title": "Updated Title"}
        response = client.put("/api/tasks/1", json=update_data)

        assert response.status_code == 403

    def test_delete_task_without_token(self, client: TestClient, sample_tasks):
        """Test DELETE /api/tasks/{id} without token returns 403"""
        response = client.delete("/api/tasks/1")

        assert response.status_code == 403

    def test_patch_task_complete_without_token(self, client: TestClient, sample_tasks):
        """Test PATCH /api/tasks/{id}/complete without token returns 403"""
        response = client.patch("/api/tasks/1/complete", json={"completed": True})

        assert response.status_code == 403


class TestCrossUserAccessProtection:
    """Tests for User Story 2 - User Data Isolation"""

    def test_cross_user_task_access_returns_403(self, client: TestClient, valid_token_user_2: str, sample_tasks):
        """T043: Test user cannot access another user's task - returns 403"""
        # User 2 tries to access User 1's task (task_id=1)
        response = client.get(
            "/api/tasks/1",
            headers={"Authorization": f"Bearer {valid_token_user_2}"}
        )

        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_cross_user_task_modification_returns_403(self, client: TestClient, valid_token_user_2: str, sample_tasks):
        """T044: Test user cannot modify another user's task - returns 403"""
        # User 2 tries to modify User 1's task (task_id=1)
        update_data = {"title": "Hacked Title"}
        response = client.put(
            "/api/tasks/1",
            json=update_data,
            headers={"Authorization": f"Bearer {valid_token_user_2}"}
        )

        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_cross_user_task_deletion_returns_403(self, client: TestClient, valid_token_user_2: str, sample_tasks):
        """T045: Test user cannot delete another user's task - returns 403"""
        # User 2 tries to delete User 1's task (task_id=1)
        response = client.delete(
            "/api/tasks/1",
            headers={"Authorization": f"Bearer {valid_token_user_2}"}
        )

        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_cross_user_task_completion_returns_403(self, client: TestClient, valid_token_user_2: str, sample_tasks):
        """T044: Test user cannot modify completion status of another user's task - returns 403"""
        # User 2 tries to mark User 1's task as complete (task_id=1)
        response = client.patch(
            "/api/tasks/1/complete",
            json={"completed": True},
            headers={"Authorization": f"Bearer {valid_token_user_2}"}
        )

        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_user_only_sees_own_tasks(self, client: TestClient, valid_token: str, valid_token_user_2: str, sample_tasks):
        """T046: Test users only see their own tasks in list operations"""
        # User 1 gets their tasks
        response_user_1 = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response_user_1.status_code == 200
        tasks_user_1 = response_user_1.json()
        assert len(tasks_user_1) == 2
        assert all(task["user_id"] == 1 for task in tasks_user_1)

        # User 2 gets their tasks
        response_user_2 = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {valid_token_user_2}"}
        )
        assert response_user_2.status_code == 200
        tasks_user_2 = response_user_2.json()
        assert len(tasks_user_2) == 1
        assert all(task["user_id"] == 2 for task in tasks_user_2)

        # Verify no overlap
        user_1_task_ids = {task["id"] for task in tasks_user_1}
        user_2_task_ids = {task["id"] for task in tasks_user_2}
        assert user_1_task_ids.isdisjoint(user_2_task_ids)

    def test_nonexistent_task_returns_404(self, client: TestClient, valid_token: str):
        """Test accessing non-existent task returns 404, not 403"""
        response = client.get(
            "/api/tasks/99999",
            headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestTokenExpiryEnforcement:
    """Tests for User Story 3 - Token Expiry Enforcement"""

    def test_expired_token_rejected_on_get_tasks(self, client: TestClient, expired_token: str, sample_tasks):
        """T051: Test expired token is rejected on GET /api/tasks"""
        response = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_expired_token_rejected_on_post_task(self, client: TestClient, expired_token: str):
        """T051: Test expired token is rejected on POST /api/tasks"""
        task_data = {"title": "New Task", "description": "Description"}
        response = client.post(
            "/api/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_expired_token_rejected_on_get_task_by_id(self, client: TestClient, expired_token: str, sample_tasks):
        """T052: Test token expiry is checked on GET /api/tasks/{id}"""
        response = client.get(
            "/api/tasks/1",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_expired_token_rejected_on_put_task(self, client: TestClient, expired_token: str, sample_tasks):
        """T052: Test token expiry is checked on PUT /api/tasks/{id}"""
        update_data = {"title": "Updated Title"}
        response = client.put(
            "/api/tasks/1",
            json=update_data,
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_expired_token_rejected_on_delete_task(self, client: TestClient, expired_token: str, sample_tasks):
        """T052: Test token expiry is checked on DELETE /api/tasks/{id}"""
        response = client.delete(
            "/api/tasks/1",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_expired_token_rejected_on_patch_complete(self, client: TestClient, expired_token: str, sample_tasks):
        """T052: Test token expiry is checked on PATCH /api/tasks/{id}/complete"""
        response = client.patch(
            "/api/tasks/1/complete",
            json={"completed": True},
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_valid_token_continues_to_work(self, client: TestClient, valid_token: str, sample_tasks):
        """T051: Test valid non-expired tokens continue to work"""
        response = client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)


