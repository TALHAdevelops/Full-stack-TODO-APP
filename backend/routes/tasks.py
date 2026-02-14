from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from models import Task
from schemas import (
    TaskCreate, TaskUpdate, TaskResponse,
    RecurrenceRequest, DueDateRequest,
    ReminderCreateRequest, ReminderResponse,
)
from db import get_session
from auth import verify_token
from services import event_publisher
from services.event_log import log_event_from_publish
from services.scheduler import calculate_next_occurrence
from models import Reminder

router = APIRouter(prefix="/api", tags=["tasks"])


async def _publish_task_event(event_type: str, user_id: str, task: Task):
    """Helper to publish a task event and log it."""
    data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "is_recurring": task.is_recurring,
        "recurrence_rule": task.recurrence_rule,
    }
    event = await event_publisher.publish_task_event(
        event_type=event_type,
        user_id=user_id,
        task_id=task.id,
        data=data,
    )
    # Also log inline for audit trail (ensures logging even if Kafka down)
    from schemas import TaskEvent
    log_data = TaskEvent(
        event_type=event_type,
        user_id=user_id,
        aggregate_id=str(task.id),
        data=data,
    )
    await log_event_from_publish(log_data.model_dump(mode="json"))


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
        description=task_data.description or "",
        due_date=task_data.due_date,
        recurrence_rule=task_data.recurrence_rule,
        is_recurring=bool(task_data.recurrence_rule),
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    await _publish_task_event("task.created", user_id, task)

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

    await _publish_task_event("task.updated", user_id, task)

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

    await _publish_task_event("task.deleted", user_id, task)

    # Cancel pending reminders before deleting
    await _cancel_pending_reminders(session, task_id)

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

    event_type = "task.completed" if task.completed else "task.uncompleted"
    await _publish_task_event(event_type, user_id, task)

    return task


# ==================== Phase 5: Recurring Tasks ====================

# SET RECURRENCE
@router.post("/tasks/{task_id}/recurrence", response_model=TaskResponse)
async def set_recurrence(
    task_id: int,
    data: RecurrenceRequest,
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token),
):
    """Set recurrence rule on a task."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.recurrence_rule = data.recurrence_rule
    task.is_recurring = True
    task.next_occurrence = calculate_next_occurrence(data.recurrence_rule)
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    await _publish_task_event("task.recurrence_set", user_id, task)
    return task


# LIST RECURRING TASKS
@router.get("/tasks/recurring", response_model=List[TaskResponse])
async def list_recurring_tasks(
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token),
):
    """List all recurring tasks for authenticated user."""
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.is_recurring == True,
    ).order_by(Task.next_occurrence)
    tasks = session.exec(statement).all()
    return tasks


# REMOVE RECURRENCE
@router.delete("/tasks/{task_id}/recurrence", response_model=TaskResponse)
async def remove_recurrence(
    task_id: int,
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token),
):
    """Remove recurrence from a task."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.recurrence_rule = None
    task.is_recurring = False
    task.next_occurrence = None
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    await _publish_task_event("task.recurrence_removed", user_id, task)
    return task


# ==================== Phase 5: Due Dates & Reminders ====================

# SET DUE DATE
@router.put("/tasks/{task_id}/due-date", response_model=TaskResponse)
async def set_due_date(
    task_id: int,
    data: DueDateRequest,
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token),
):
    """Set or update due date on a task."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.due_date = data.due_date
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

    await _publish_task_event("task.due_date_changed", user_id, task)
    return task


# CREATE REMINDER
@router.post("/tasks/{task_id}/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    task_id: int,
    data: ReminderCreateRequest,
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token),
):
    """Create a reminder for a task."""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    reminder = Reminder(
        task_id=task_id,
        user_id=user_id,
        remind_at=data.remind_at,
    )
    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return reminder


# LIST PENDING REMINDERS
@router.get("/reminders/pending", response_model=List[ReminderResponse])
async def list_pending_reminders(
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token),
):
    """List all pending (not notified) reminders for authenticated user."""
    statement = select(Reminder).where(
        Reminder.user_id == user_id,
        Reminder.notified == False,
    ).order_by(Reminder.remind_at)
    reminders = session.exec(statement).all()
    return reminders


# CANCEL REMINDERS ON TASK DELETE/COMPLETE
async def _cancel_pending_reminders(session: Session, task_id: int):
    """Cancel all pending reminders for a task (called on delete/complete)."""
    statement = select(Reminder).where(
        Reminder.task_id == task_id,
        Reminder.notified == False,
    )
    reminders = session.exec(statement).all()
    for reminder in reminders:
        reminder.notified = True  # Mark as notified to prevent triggering
        session.add(reminder)
    if reminders:
        session.commit()
