from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session
from typing import List
from src.database.database import get_session
from src.models.task_model import Task, TaskCreate, TaskUpdate, TaskRead
from src.services.task_service import (
    create_task,
    get_tasks_by_user,
    get_task_by_id_and_user,
    update_task,
    delete_task,
    update_task_completion_status
)
from pydantic import BaseModel

router = APIRouter()


# Define a simple model for the patch request
class TaskCompleteRequest(BaseModel):
    completed: bool


@router.get("/tasks", response_model=List[TaskRead])
def get_tasks(user_id: int, session: Session = Depends(get_session)):
    """
    Get all tasks for a user
    """
    tasks = get_tasks_by_user(session, user_id)
    return tasks


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_new_task(user_id: int, task_data: TaskCreate, session: Session = Depends(get_session)):
    """
    Create a new task for a user
    """
    # Add user_id to the task data
    task_dict = task_data.dict()
    task_dict['user_id'] = user_id

    # Validate that the user_id in the request body matches the path parameter
    if task_data.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID in request body must match user ID in path"
        )

    try:
        task = create_task(session, task_dict)
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(user_id: int, task_id: int, session: Session = Depends(get_session)):
    """
    Get a specific task by ID
    """
    task = get_task_by_id_and_user(session, task_id, user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_existing_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session)
):
    """
    Update a specific task
    """
    # Check if the task exists for the user
    existing_task = get_task_by_id_and_user(session, task_id, user_id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Prepare update data (only include non-None values)
    update_data = {}
    task_dict = task_data.dict(exclude_unset=True)
    for field, value in task_dict.items():
        if value is not None:
            update_data[field] = value

    # If user_id is in the update data, validate it matches the path parameter
    if 'user_id' in update_data and update_data['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change task owner"
        )

    # Update the task
    updated_task = update_task(session, task_id, user_id, update_data)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return updated_task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(user_id: int, task_id: int, session: Session = Depends(get_session)):
    """
    Delete a specific task
    """
    success = delete_task(session, task_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return {"detail": "Task deleted successfully"}


from fastapi import Body

# Define a simple model for the patch request
from pydantic import BaseModel
class TaskCompleteRequest(BaseModel):
    completed: bool

@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
def update_task_complete_status(
    user_id: int,
    task_id: int,
    request: TaskCompleteRequest = Body(...),
    session: Session = Depends(get_session)
):
    """
    Mark a task as complete/incomplete based on the request body
    """
    # Get the existing task to check if it exists
    existing_task = get_task_by_id_and_user(session, task_id, user_id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update the task with the new completion status from the request
    updated_task = update_task_completion_status(session, task_id, user_id, request.completed)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return updated_task