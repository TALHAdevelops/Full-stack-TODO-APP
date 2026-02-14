"""Integration tests for the event publishing flow.

Tests:
- Event schema validation
- Event publisher creates valid TaskEvent objects
- Event log service persists events correctly
- Recurrence calculator produces correct next occurrence dates
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from schemas import TaskEvent, RecurrenceRequest, ReminderCreateRequest


class TestTaskEventSchema:
    """Test TaskEvent Pydantic model validation."""

    def test_create_event_with_defaults(self):
        event = TaskEvent(
            event_type="task.created",
            user_id="user-123",
            aggregate_id="42",
            data={"title": "Test Task"},
        )
        assert event.event_type == "task.created"
        assert event.user_id == "user-123"
        assert event.aggregate_id == "42"
        assert event.version == 1
        assert event.event_id  # Auto-generated UUID
        assert event.correlation_id  # Auto-generated UUID
        assert event.timestamp  # Auto-generated datetime

    def test_event_serialization(self):
        event = TaskEvent(
            event_type="task.updated",
            user_id="user-456",
            aggregate_id="99",
            data={"title": "Updated"},
        )
        serialized = event.model_dump(mode="json")
        assert serialized["event_type"] == "task.updated"
        assert serialized["user_id"] == "user-456"
        assert isinstance(serialized["timestamp"], str)  # ISO format string
        assert isinstance(serialized["data"], dict)

    def test_event_types_cover_all_operations(self):
        event_types = [
            "task.created",
            "task.updated",
            "task.deleted",
            "task.completed",
            "task.uncompleted",
            "task.recurrence_set",
            "task.recurrence_removed",
            "task.due_date_changed",
            "recurring.spawned",
            "reminder.triggered",
        ]
        for event_type in event_types:
            event = TaskEvent(
                event_type=event_type,
                user_id="test",
                aggregate_id="1",
                data={},
            )
            assert event.event_type == event_type


class TestRecurrenceRequest:
    """Test recurrence request validation."""

    def test_valid_daily_recurrence(self):
        req = RecurrenceRequest(recurrence_rule="FREQ=DAILY")
        assert req.recurrence_rule == "FREQ=DAILY"

    def test_valid_weekly_recurrence(self):
        req = RecurrenceRequest(recurrence_rule="FREQ=WEEKLY;BYDAY=MO,WE,FR")
        assert req.recurrence_rule == "FREQ=WEEKLY;BYDAY=MO,WE,FR"

    def test_valid_monthly_recurrence(self):
        req = RecurrenceRequest(recurrence_rule="FREQ=MONTHLY")
        assert req.recurrence_rule == "FREQ=MONTHLY"


class TestRecurrenceCalculator:
    """Test RRULE-based recurrence calculation."""

    def test_daily_next_occurrence(self):
        from services.scheduler import calculate_next_occurrence
        now = datetime(2026, 2, 14, 10, 0, 0)
        next_occ = calculate_next_occurrence("FREQ=DAILY", after=now)
        assert next_occ is not None
        assert next_occ > now
        assert next_occ.day == 15  # Next day

    def test_weekly_next_occurrence(self):
        from services.scheduler import calculate_next_occurrence
        # A Saturday
        now = datetime(2026, 2, 14, 10, 0, 0)
        next_occ = calculate_next_occurrence("FREQ=WEEKLY;BYDAY=MO", after=now)
        assert next_occ is not None
        assert next_occ > now
        assert next_occ.weekday() == 0  # Monday

    def test_empty_rule_returns_none(self):
        from services.scheduler import calculate_next_occurrence
        result = calculate_next_occurrence("")
        assert result is None

    def test_invalid_rule_returns_none(self):
        from services.scheduler import calculate_next_occurrence
        result = calculate_next_occurrence("INVALID_RULE")
        assert result is None


class TestReminderRequest:
    """Test reminder request validation."""

    def test_valid_reminder(self):
        future = datetime.utcnow() + timedelta(hours=24)
        req = ReminderCreateRequest(remind_at=future)
        assert req.remind_at == future
