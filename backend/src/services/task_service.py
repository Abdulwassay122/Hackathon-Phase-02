from typing import List, Optional
from sqlmodel import Session, select
from src.models.task_model import Task, TaskCreate, TaskUpdate
from datetime import datetime


def create_task(session: Session, task_data: dict) -> Task:
    """
    Create a new task in the database
    """
    # Create task object from data
    task = Task(
        title=task_data['title'],
        description=task_data.get('description'),
        completed=task_data.get('completed', False),
        user_id=task_data['user_id']
    )

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_tasks_by_user(session: Session, user_id: int) -> List[Task]:
    """
    Get all tasks for a specific user
    """
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks


def get_task_by_id(session: Session, task_id: int) -> Optional[Task]:
    """
    Get a specific task by ID (without user filtering)
    Used for ownership verification
    """
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    return task


def get_task_by_id_and_user(session: Session, task_id: int, user_id: int) -> Optional[Task]:
    """
    Get a specific task by ID and user ID
    Verifies ownership by filtering on both task_id and user_id
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    return task


def update_task(session: Session, task_id: int, user_id: int, task_data: dict) -> Optional[Task]:
    """
    Update a specific task for a user
    """
    task = get_task_by_id_and_user(session, task_id, user_id)
    if not task:
        return None

    # Update only provided fields
    for field, value in task_data.items():
        if value is not None:
            setattr(task, field, value)

    # Update the timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task_id: int, user_id: int) -> bool:
    """
    Delete a specific task for a user
    """
    task = get_task_by_id_and_user(session, task_id, user_id)
    if not task:
        return False

    session.delete(task)
    session.commit()
    return True


def update_task_completion_status(session: Session, task_id: int, user_id: int, completed: bool) -> Optional[Task]:
    """
    Update the completion status of a specific task for a user
    """
    task = get_task_by_id_and_user(session, task_id, user_id)
    if not task:
        return None

    task.completed = completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    return task