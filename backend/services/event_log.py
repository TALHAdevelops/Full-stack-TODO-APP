"""Event logging service for audit trail persistence to database.

Stores all published events in the event_log table for replay and auditing.
Registered as a wildcard handler in the event processor.
"""

import json
import logging

from sqlmodel import Session

from db import engine
from models import EventLog

logger = logging.getLogger(__name__)


async def log_event(event_data: dict):
    """Persist an event to the event_log table.

    This is registered as a '*' handler in the event processor,
    so it receives ALL events for audit trail purposes.
    """
    try:
        with Session(engine) as session:
            log_entry = EventLog(
                event_id=event_data.get("event_id", ""),
                event_type=event_data.get("event_type", "unknown"),
                user_id=event_data.get("user_id", ""),
                aggregate_id=event_data.get("aggregate_id", ""),
                correlation_id=event_data.get("correlation_id", ""),
                data=json.dumps(event_data.get("data", {})),
                version=event_data.get("version", 1),
            )
            session.add(log_entry)
            session.commit()
            logger.debug("Event logged: event_type=%s aggregate_id=%s", log_entry.event_type, log_entry.aggregate_id)
    except Exception as e:
        logger.error("Failed to log event: %s", e)


async def log_event_from_publish(event_data: dict):
    """Log an event directly after publishing (inline, not via consumer).

    Used to ensure events are logged even when Kafka is unavailable.
    """
    await log_event(event_data)
