"""Event consumer infrastructure with topic subscription and callback dispatch.

Manages event consumption from Kafka topics and routes events to registered handlers.
Supports both Dapr subscription endpoints and direct Kafka consumers.
"""

import logging
from typing import Callable, Dict, List, Optional

from config import settings
from services import kafka_client

logger = logging.getLogger(__name__)

# Registry of event handlers: event_type -> list of callbacks
_handlers: Dict[str, List[Callable]] = {}


def register_handler(event_type: str, handler: Callable):
    """Register a handler for a specific event type.

    Args:
        event_type: Event type to handle (e.g., "task.created", "*" for all)
        handler: Async callable that receives event data dict
    """
    if event_type not in _handlers:
        _handlers[event_type] = []
    _handlers[event_type].append(handler)
    logger.info("Registered handler for event_type=%s: %s", event_type, handler.__name__)


async def dispatch_event(event_data: dict):
    """Dispatch an event to all registered handlers matching its event_type."""
    event_type = event_data.get("event_type", "unknown")

    # Call specific handlers for this event type
    handlers = _handlers.get(event_type, [])
    # Also call wildcard handlers
    handlers += _handlers.get("*", [])

    for handler in handlers:
        try:
            await handler(event_data)
        except Exception as e:
            logger.error(
                "Handler %s failed for event_type=%s: %s",
                handler.__name__,
                event_type,
                e,
            )


async def start_consumers():
    """Start Kafka consumers for all event topics.

    When USE_DAPR=true, Dapr handles subscription via its sidecar.
    When USE_DAPR=false, we create direct Kafka consumers.
    """
    if settings.USE_DAPR:
        logger.info("Dapr mode: event consumption handled by Dapr subscription endpoints")
        return

    # Direct Kafka consumers
    await kafka_client.create_consumer(
        topic="tasks.events",
        group_id="taskflow-event-processor",
        callback=dispatch_event,
    )

    await kafka_client.create_consumer(
        topic="reminders",
        group_id="taskflow-reminder-processor",
        callback=dispatch_event,
    )

    logger.info("Direct Kafka consumers started for tasks.events and reminders topics")


async def stop_consumers():
    """Stop all consumers."""
    await kafka_client.stop_all()
    logger.info("Event consumers stopped")
