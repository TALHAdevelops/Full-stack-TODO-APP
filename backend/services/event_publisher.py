"""Dual-path EventPublisher: Dapr pub/sub when USE_DAPR=true, direct Kafka otherwise.

Provides a single publish() interface that routes events through the appropriate path.
Gracefully degrades if neither Kafka nor Dapr is available.
"""

import logging
from typing import Optional

from config import settings
from schemas import TaskEvent
from services import kafka_client
from services.dapr_client import publish_event_dapr

logger = logging.getLogger(__name__)

# Topic for all task-related events
TASKS_EVENTS_TOPIC = "tasks.events"
REMINDERS_TOPIC = "reminders"


async def publish(event: TaskEvent, topic: str = TASKS_EVENTS_TOPIC) -> bool:
    """Publish a TaskEvent to the event bus.

    Routes through Dapr (if USE_DAPR=true) or direct Kafka.
    Returns True if event was published, False if delivery failed (graceful degradation).
    """
    event_data = event.model_dump(mode="json")

    if settings.USE_DAPR:
        success = await publish_event_dapr(topic, event_data)
        if success:
            return True
        # Fallback to direct Kafka if Dapr fails
        logger.warning("Dapr publish failed, falling back to direct Kafka")

    # Direct Kafka path
    success = await kafka_client.publish_message(
        topic=topic,
        value=event_data,
        key=event.user_id,
    )

    if not success:
        logger.warning(
            "Event not delivered (Kafka unavailable): event_type=%s aggregate_id=%s",
            event.event_type,
            event.aggregate_id,
        )

    return success


async def publish_task_event(
    event_type: str,
    user_id: str,
    task_id: int,
    data: dict,
    correlation_id: Optional[str] = None,
) -> bool:
    """Convenience method to publish a task event."""
    event = TaskEvent(
        event_type=event_type,
        user_id=user_id,
        aggregate_id=str(task_id),
        data=data,
    )
    if correlation_id:
        event.correlation_id = correlation_id

    return await publish(event, topic=TASKS_EVENTS_TOPIC)


async def publish_reminder_event(
    user_id: str,
    reminder_id: str,
    task_id: int,
    data: dict,
) -> bool:
    """Publish a reminder event."""
    event = TaskEvent(
        event_type="reminder.triggered",
        user_id=user_id,
        aggregate_id=str(reminder_id),
        data=data,
    )
    return await publish(event, topic=REMINDERS_TOPIC)
