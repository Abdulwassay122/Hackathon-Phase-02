from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session
from typing import List
import logging
from src.database.database import get_session
from src.models.task_model import Task, TaskCreate, TaskUpdate, TaskRead
from src.services.task_service import (
    create_task,
    get_tasks_by_user,
    get_task_by_id,
    get_task_by_id_and_user,
    update_task,
    delete_task,
    update_task_completion_status
)
from src.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()

# T042: Security logging for unauthorized access attempts
logger = logging.getLogger(__name__)


# Define a simple model for the patch request
class TaskCompleteRequest(BaseModel):
    completed: bool


@router.get("/tasks", response_model=List[TaskRead])
def get_tasks(
    current_user: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for the authenticated user

    Authentication: Required (JWT Bearer token)
    """
    tasks = get_tasks_by_user(session, current_user)
    return tasks


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_data: TaskCreate,
    current_user: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user

    Authentication: Required (JWT Bearer token)
    Note: user_id is automatically set from the authenticated user
    """
    # Automatically set user_id from authenticated user
    task_dict = task_data.dict()
    task_dict['user_id'] = current_user

    try:
        task = create_task(session, task_dict)
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    current_user: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID

    Authentication: Required (JWT Bearer token)
    Authorization: User must own the task
    """
    # T033: Check if task exists first
    task = get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # T040: Verify ownership - return 403 if user doesn't own the task
    if task.user_id != current_user:
        # T042: Log unauthorized access attempt
        logger.warning(
            f"Unauthorized access attempt: User {current_user} attempted to access task {task_id} owned by user {task.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this task"
        )

    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_existing_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task

    Authentication: Required (JWT Bearer token)
    Authorization: User must own the task
    """
    # T034: Check if task exists first
    existing_task = get_task_by_id(session, task_id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # T041: Verify ownership - return 403 if user doesn't own the task
    if existing_task.user_id != current_user:
        # T042: Log unauthorized modification attempt
        logger.warning(
            f"Unauthorized modification attempt: User {current_user} attempted to modify task {task_id} owned by user {existing_task.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task"
        )

    # Prepare update data (only include non-None values)
    update_data = {}
    task_dict = task_data.dict(exclude_unset=True)
    for field, value in task_dict.items():
        if value is not None:
            update_data[field] = value

    # T039: Prevent user_id modification
    if 'user_id' in update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change task owner"
        )

    # Update the task
    updated_task = update_task(session, task_id, current_user, update_data)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return updated_task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(
    task_id: int,
    current_user: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task

    Authentication: Required (JWT Bearer token)
    Authorization: User must own the task
    """
    # T035: Check if task exists first
    existing_task = get_task_by_id(session, task_id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # T041: Verify ownership - return 403 if user doesn't own the task
    if existing_task.user_id != current_user:
        # T042: Log unauthorized deletion attempt
        logger.warning(
            f"Unauthorized deletion attempt: User {current_user} attempted to delete task {task_id} owned by user {existing_task.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this task"
        )

    # Delete the task
    success = delete_task(session, task_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return {"detail": "Task deleted successfully"}


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
def update_task_complete_status(
    task_id: int,
    request: TaskCompleteRequest = Body(...),
    current_user: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Mark a task as complete/incomplete based on the request body

    Authentication: Required (JWT Bearer token)
    Authorization: User must own the task
    """
    # T036: Check if task exists first
    existing_task = get_task_by_id(session, task_id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # T041: Verify ownership - return 403 if user doesn't own the task
    if existing_task.user_id != current_user:
        # T042: Log unauthorized modification attempt
        logger.warning(
            f"Unauthorized modification attempt: User {current_user} attempted to modify completion status of task {task_id} owned by user {existing_task.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this task"
        )

    # Update the task with the new completion status from the request
    updated_task = update_task_completion_status(session, task_id, current_user, request.completed)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return updated_task