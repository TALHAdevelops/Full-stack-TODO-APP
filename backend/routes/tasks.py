from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse
from db import get_session
from auth import verify_token

router = APIRouter(prefix="/api", tags=["tasks"])

# LIST TASKS
@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token)
):
    """List all tasks for authenticated user"""
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return tasks

# CREATE TASK
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token)
):
    """Create new task"""
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description or ""
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# GET SINGLE TASK
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token)
):
    """Get task by ID"""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task

# UPDATE TASK
@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token)
):
    """Update task"""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# DELETE TASK
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token)
):
    """Delete task"""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    session.delete(task)
    session.commit()
    return None

# TOGGLE TASK STATUS
@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_status(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token)
):
    """Toggle task completion status"""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
