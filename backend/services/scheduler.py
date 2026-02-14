"""Scheduler service: RRULE recurrence calculation, APScheduler jobs for recurring tasks and reminders.

Handles:
- Recurrence calculation via dateutil.rrule
- Spawning new task instances from recurring patterns
- Checking and triggering pending reminders
"""

import logging
from datetime import datetime, timezone

from dateutil.rrule import rrulestr
from sqlmodel import Session, select

from db import engine
from models import Task, Reminder
from services import event_publisher

logger = logging.getLogger(__name__)


def calculate_next_occurrence(recurrence_rule: str, after: datetime = None) -> datetime | None:
    """Calculate next occurrence from an RRULE string.

    Args:
        recurrence_rule: RRULE format string (e.g., "FREQ=DAILY", "FREQ=WEEKLY;BYDAY=MO,WE")
        after: Calculate next occurrence after this time (default: now UTC)

    Returns:
        Next occurrence datetime, or None if no more occurrences
    """
    if not recurrence_rule:
        return None

    if after is None:
        after = datetime.now(timezone.utc)

    try:
        rule = rrulestr(f"RRULE:{recurrence_rule}", dtstart=after)
        # Get the next occurrence after 'after'
        next_occ = rule.after(after, inc=False)
        return next_occ
    except Exception as e:
        logger.error("Failed to parse RRULE '%s': %s", recurrence_rule, e)
        return None


async def spawn_recurring_tasks():
    """Check for recurring tasks due and spawn new instances.

    Called every minute by APScheduler or Dapr cron binding.
    """
    now = datetime.utcnow()

    try:
        with Session(engine) as session:
            # Find recurring tasks where next_occurrence is due
            statement = select(Task).where(
                Task.is_recurring == True,
                Task.next_occurrence != None,
                Task.next_occurrence <= now,
            )
            due_tasks = session.exec(statement).all()

            for task in due_tasks:
                try:
                    # Create new task instance
                    new_task = Task(
                        user_id=task.user_id,
                        title=task.title,
                        description=task.description,
                        due_date=task.next_occurrence,
                    )
                    session.add(new_task)

                    # Calculate next occurrence
                    next_occ = calculate_next_occurrence(task.recurrence_rule, after=task.next_occurrence)
                    task.next_occurrence = next_occ

                    session.add(task)
                    session.commit()
                    session.refresh(new_task)

                    # Publish event
                    await event_publisher.publish_task_event(
                        event_type="recurring.spawned",
                        user_id=task.user_id,
                        task_id=new_task.id,
                        data={
                            "id": new_task.id,
                            "title": new_task.title,
                            "parent_task_id": task.id,
                            "recurrence_rule": task.recurrence_rule,
                        },
                    )

                    logger.info(
                        "Spawned recurring task: id=%d from parent=%d next=%s",
                        new_task.id, task.id, next_occ,
                    )
                except Exception as e:
                    logger.error("Failed to spawn recurring task %d: %s", task.id, e)
                    session.rollback()

    except Exception as e:
        logger.error("spawn_recurring_tasks failed: %s", e)


async def check_pending_reminders():
    """Check for pending reminders and publish notification events.

    Called every minute by APScheduler or Dapr cron binding.
    Uses 'notified' flag for idempotency — prevents duplicate notifications.
    """
    now = datetime.utcnow()

    try:
        with Session(engine) as session:
            # Find reminders that are due and not yet notified
            statement = select(Reminder).where(
                Reminder.notified == False,
                Reminder.remind_at <= now,
            )
            pending = session.exec(statement).all()

            for reminder in pending:
                try:
                    # Get the associated task for context
                    task = session.get(Task, reminder.task_id)
                    task_title = task.title if task else "Unknown task"

                    # Publish reminder event
                    await event_publisher.publish_reminder_event(
                        user_id=reminder.user_id,
                        reminder_id=str(reminder.id),
                        task_id=reminder.task_id,
                        data={
                            "reminder_id": str(reminder.id),
                            "task_id": reminder.task_id,
                            "task_title": task_title,
                            "remind_at": reminder.remind_at.isoformat(),
                        },
                    )

                    # Mark as notified (idempotency)
                    reminder.notified = True
                    session.add(reminder)
                    session.commit()

                    logger.info(
                        "Reminder triggered: id=%s task=%d user=%s",
                        reminder.id, reminder.task_id, reminder.user_id,
                    )
                except Exception as e:
                    logger.error("Failed to process reminder %s: %s", reminder.id, e)
                    session.rollback()

    except Exception as e:
        logger.error("check_pending_reminders failed: %s", e)
