"""WebSocket event handler: bridges Kafka events to WebSocket broadcasts.

Registered as an event handler for task events. When a task event is received,
it broadcasts the event to all connected WebSocket clients for that user.
"""

import logging

from services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


async def on_task_event(event_data: dict):
    """Handle a task event by broadcasting it to the user's WebSocket connections."""
    user_id = event_data.get("user_id")
    if not user_id:
        return

    message = {
        "type": event_data.get("event_type", "unknown"),
        "data": event_data.get("data", {}),
        "timestamp": event_data.get("timestamp", ""),
        "correlation_id": event_data.get("correlation_id", ""),
        "event_id": event_data.get("event_id", ""),
    }

    await ws_manager.broadcast_to_user(user_id, message)
    logger.debug(
        "Broadcast to user %s: event_type=%s connections=%d",
        user_id,
        message["type"],
        ws_manager.get_connection_count(user_id),
    )
