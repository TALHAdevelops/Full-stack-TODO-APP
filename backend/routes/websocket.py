"""WebSocket endpoint at /ws/user/{user_id}/tasks with JWT validation on connect."""

import asyncio
import logging

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config import settings
from services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


def _verify_ws_token(token: str) -> str:
    """Verify JWT token from WebSocket query params. Returns user_id."""
    try:
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing sub claim")
        return user_id
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {e}")


@router.websocket("/ws/user/{user_id}/tasks")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time task updates.

    Connect with: ws://host/ws/user/{user_id}/tasks?token=JWT_TOKEN
    """
    # 1. Extract and validate JWT token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    try:
        token_user_id = _verify_ws_token(token)
    except ValueError as e:
        await websocket.accept()  # Must accept before close with reason
        await websocket.close(code=4001, reason=str(e))
        return

    # 2. Verify user_id matches token
    if token_user_id != user_id:
        await websocket.accept()
        await websocket.close(code=4003, reason="Unauthorized: user mismatch")
        return

    # 3. Accept connection
    await websocket.accept()
    ws_manager.add_connection(user_id, websocket)

    try:
        # 4. Keep connection alive with ping/pong
        while True:
            try:
                # Wait for client messages (ping/pong) or disconnect
                data = await asyncio.wait_for(websocket.receive_text(), timeout=45)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send server-side ping to keep alive
                try:
                    await websocket.send_text("ping")
                except Exception:
                    break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.debug("WebSocket error for user %s: %s", user_id, e)
    finally:
        ws_manager.remove_connection(user_id, websocket)
