from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default="", max_length=1000)
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None  # RRULE format: "FREQ=DAILY", "FREQ=WEEKLY;BYDAY=MO"

class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class TaskResponse(BaseModel):
    """Schema for task response"""
    id: int
    user_id: str
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    recurrence_rule: Optional[str] = None
    is_recurring: bool = False
    next_occurrence: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RecurrenceRequest(BaseModel):
    """Schema for setting recurrence on a task"""
    recurrence_rule: str = Field(min_length=1)  # "FREQ=DAILY", "FREQ=WEEKLY;BYDAY=MO,WE,FR"

class DueDateRequest(BaseModel):
    """Schema for setting a due date on a task"""
    due_date: datetime

class ReminderCreateRequest(BaseModel):
    """Schema for creating a reminder"""
    remind_at: datetime

class ReminderResponse(BaseModel):
    """Schema for reminder response"""
    id: UUID
    task_id: int
    user_id: str
    remind_at: datetime
    notified: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Event schemas
class TaskEvent(BaseModel):
    """Schema for Kafka task events"""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str  # "task.created", "task.updated", "task.deleted", etc.
    user_id: str
    aggregate_id: str  # task_id as string
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    data: dict = Field(default_factory=dict)
    version: int = 1

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
