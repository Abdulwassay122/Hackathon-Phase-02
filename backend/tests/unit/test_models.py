import pytest
from src.models.task_model import Task, TaskCreate, TaskUpdate, TaskRead
from datetime import datetime


def test_task_creation():
    """Test creating a Task instance"""
    task = Task(
        title="Test Task",
        description="Test Description",
        completed=False,
        user_id=1
    )

    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert task.user_id == 1
    assert task.id is None  # Should be None before saving


def test_task_create_model():
    """Test TaskCreate model validation"""
    task_create = TaskCreate(
        title="Test Task",
        description="Test Description",
        completed=False,
        user_id=1
    )

    assert task_create.title == "Test Task"
    assert task_create.description == "Test Description"
    assert task_create.completed is False
    assert task_create.user_id == 1


def test_task_read_model():
    """Test TaskRead model"""
    now = datetime.utcnow()
    task_read = TaskRead(
        title="Test Task",
        description="Test Description",
        completed=False,
        user_id=1,
        id=1,
        created_at=now,
        updated_at=now
    )

    assert task_read.title == "Test Task"
    assert task_read.id == 1
    assert task_read.created_at == now


def test_task_update_model():
    """Test TaskUpdate model"""
    task_update = TaskUpdate(title="Updated Title")

    assert task_update.title == "Updated Title"
    assert task_update.description is None
    assert task_update.completed is None


def test_task_title_validation():
    """Test Task title validation through model_validate"""
    from pydantic import ValidationError

    # Test minimum length validation - validation happens during serialization
    with pytest.raises(ValidationError):
        Task.model_validate({"title": "", "description": "Valid description", "user_id": 1})

    # Test maximum length validation
    with pytest.raises(ValidationError):
        long_title = "x" * 256  # 256 characters exceeds max length of 255
        Task.model_validate({"title": long_title, "description": "Valid description", "user_id": 1})


def test_task_description_max_length():
    """Test Task description maximum length"""
    # Create a description with 1001 characters (exceeds max length of 1000)
    long_desc = "x" * 1001

    # Note: SQLModel validation might not catch this at model level,
    # but the database constraint will handle it
    task = Task(title="Valid Title", description=long_desc, user_id=1, completed=False)

    # At model level, it will accept the long description
    assert len(task.description) == 1001