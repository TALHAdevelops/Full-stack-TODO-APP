"""WebSocket connection manager: per-user rooms, add/remove/broadcast.

Manages active WebSocket connections grouped by user_id for targeted event delivery.
"""

import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections per user for real-time event delivery."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    def add_connection(self, user_id: str, websocket: WebSocket):
        """Add a WebSocket connection for a user."""
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info("WebSocket connected: user_id=%s (total=%d)", user_id, len(self.active_connections[user_id]))

    def remove_connection(self, user_id: str, websocket: WebSocket):
        """Remove a WebSocket connection for a user."""
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info("WebSocket disconnected: user_id=%s", user_id)

    async def broadcast_to_user(self, user_id: str, message: dict):
        """Send a message to all connected WebSocket clients for a user."""
        if user_id not in self.active_connections:
            return

        dead_connections = []
        for ws in self.active_connections[user_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead_connections.append(ws)

        # Clean up dead connections
        for ws in dead_connections:
            self.remove_connection(user_id, ws)

    def get_connection_count(self, user_id: str = None) -> int:
        """Get number of active connections (for a user or total)."""
        if user_id:
            return len(self.active_connections.get(user_id, []))
        return sum(len(conns) for conns in self.active_connections.values())


# Singleton instance
ws_manager = WebSocketManager()
