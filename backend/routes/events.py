"""Event history API routes for audit trail querying."""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from models import EventLog
from db import get_session
from auth import verify_token

router = APIRouter(prefix="/api", tags=["events"])


@router.get("/events")
async def list_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    aggregate_id: Optional[str] = Query(None, description="Filter by aggregate (task) ID"),
    since: Optional[datetime] = Query(None, description="Filter events after this timestamp"),
    until: Optional[datetime] = Query(None, description="Filter events before this timestamp"),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token),
):
    """Query event history for authenticated user.

    Supports filtering by event_type, aggregate_id, and time range.
    Results are ordered by timestamp descending (newest first).
    """
    statement = select(EventLog).where(EventLog.user_id == user_id)

    if event_type:
        statement = statement.where(EventLog.event_type == event_type)
    if aggregate_id:
        statement = statement.where(EventLog.aggregate_id == aggregate_id)
    if since:
        statement = statement.where(EventLog.timestamp >= since)
    if until:
        statement = statement.where(EventLog.timestamp <= until)

    statement = statement.order_by(EventLog.timestamp.desc()).limit(limit)
    events = session.exec(statement).all()

    return [
        {
            "id": str(e.id),
            "event_id": e.event_id,
            "event_type": e.event_type,
            "user_id": e.user_id,
            "aggregate_id": e.aggregate_id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "correlation_id": e.correlation_id,
            "data": e.data,
            "version": e.version,
        }
        for e in events
    ]


@router.get("/tasks/{task_id}/events")
async def list_task_events(
    task_id: int,
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session),
    user_id: str = Depends(verify_token),
):
    """Get event history for a specific task.

    Returns all events with aggregate_id matching the task_id,
    ordered by timestamp ascending (oldest first, for replay).
    """
    statement = (
        select(EventLog)
        .where(
            EventLog.user_id == user_id,
            EventLog.aggregate_id == str(task_id),
        )
        .order_by(EventLog.timestamp.asc())
        .limit(limit)
    )
    events = session.exec(statement).all()

    return [
        {
            "id": str(e.id),
            "event_id": e.event_id,
            "event_type": e.event_type,
            "user_id": e.user_id,
            "aggregate_id": e.aggregate_id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "correlation_id": e.correlation_id,
            "data": e.data,
            "version": e.version,
        }
        for e in events
    ]
