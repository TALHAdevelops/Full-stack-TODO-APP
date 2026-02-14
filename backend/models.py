from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import JSON
import json

class User(SQLModel, table=True):
    """User model (managed by Better Auth, defined here for relationships)"""
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Task(SQLModel, table=True):
    """Task model for storing user tasks"""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase 5: Recurring tasks and reminders
    due_date: Optional[datetime] = Field(default=None, index=True)
    recurrence_rule: Optional[str] = Field(default=None)  # RRULE format
    is_recurring: bool = Field(default=False, index=True)
    next_occurrence: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    user: User = Relationship(back_populates="tasks")
    reminders: List["Reminder"] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Reminder(SQLModel, table=True):
    """Reminder model for task due-date notifications

    @spec: Phase 5 - US3 Reminders
    """
    __tablename__ = "reminders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    remind_at: datetime = Field(index=True)
    notified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    task: Task = Relationship(back_populates="reminders")


class EventLog(SQLModel, table=True):
    """Immutable event log for audit trail

    @spec: Phase 5 - US4 Event History
    """
    __tablename__ = "event_log"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    event_id: str = Field(index=True)
    event_type: str = Field(index=True)
    user_id: str = Field(index=True)
    aggregate_id: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    correlation_id: str = Field(default="")
    data: str = Field(default="{}")  # JSON string
    version: int = Field(default=1)


class Conversation(SQLModel, table=True):
    """Conversation model for storing chat conversations

    @spec: T-301 (spec.md §1.0, plan.md §1)
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Message(SQLModel, table=True):
    """Message model for storing conversation messages

    @spec: T-302 (spec.md §1.0, plan.md §1)
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    role: str = Field(index=True)  # "user" or "assistant"
    content: str
    tool_calls: Optional[str] = Field(default=None)  # JSON stored as string
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    conversation: Conversation = Relationship(back_populates="messages")
