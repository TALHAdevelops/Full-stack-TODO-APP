"""Chat endpoint for TaskFlow Phase III - AI Chatbot

@spec: T-323 to T-327 (spec.md §Chat Endpoint & FR-301-FR-351, plan.md §Chat Endpoint)
"""

import logging
import json
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from db import get_session
from auth import verify_token
from models import Conversation, Message, Task
from agents import create_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


# ===== Request/Response Models =====

class ChatRequest(BaseModel):
    """Chat endpoint request body"""
    conversation_id: Optional[str] = None
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Add buy milk"
            }
        }


class ToolCallResult(BaseModel):
    """Result of a tool invocation"""
    tool_name: str
    input: Optional[dict] = None
    result: dict


class ChatResponse(BaseModel):
    """Chat endpoint response body"""
    id: str
    conversation_id: str
    user_id: str
    content: str
    tool_calls: List[ToolCallResult]
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg-550e8400-e29b-41d4-a716-446655440000",
                "conversation_id": "conv-550e8400-e29b-41d4-a716-446655440001",
                "user_id": "user-123",
                "content": "Great! I've added 'buy milk' to your tasks.",
                "tool_calls": [
                    {
                        "tool_name": "add_task",
                        "input": {"user_id": "user-123", "title": "buy milk"},
                        "result": {"status": "success", "data": {"task_id": 5, "title": "buy milk"}}
                    }
                ],
                "created_at": "2026-01-13T10:30:00Z"
            }
        }


# ===== Helper Functions =====

def _fetch_conversation_history(
    session: Session,
    user_id: str,
    conversation_id: UUID,
    limit: int = 20
) -> List[Message]:
    """Fetch conversation history for context (last N messages)"""
    statement = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    return session.exec(statement).all()


def _build_message_context(history: List[Message]) -> list:
    """Build message context for agent (system + history + new message)"""
    messages = []

    # Add conversation history
    for msg in history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    return messages


def _store_message(
    session: Session,
    conversation_id: UUID,
    user_id: str,
    role: str,
    content: str,
    tool_calls: Optional[dict] = None
) -> Message:
    """Store a message in the database"""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def _generate_conversation_title(message: str, max_length: int = 50) -> str:
    """Auto-generate conversation title from first message"""
    title = message.strip()
    if len(title) > max_length:
        title = title[:max_length - 3] + "..."
    return title


# ===== Chat Endpoint =====

@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    token_user_id: str = Depends(verify_token)
) -> ChatResponse:
    """
    Main chat endpoint for AI-powered task management.

    **Authentication**: Requires valid JWT token in Authorization header
    **User Isolation**: Verifies token user_id matches path parameter

    @spec: T-323 to T-327 (spec.md FR-301-FR-310)
    """
    try:
        # 1. Validate JWT and user_id match (FR-303, FR-305)
        if token_user_id != user_id:
            logger.warning(f"User ID mismatch: token={token_user_id}, path={user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User ID mismatch"
            )

        # 2. Validate message input (FR-308, FR-309)
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        if len(request.message) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message exceeds 5000 character limit"
            )

        user_message = request.message.strip()

        # 3. Handle conversation (create or fetch) (FR-310, FR-311)
        conversation_id = None
        conversation = None

        if request.conversation_id:
            try:
                conversation_id = UUID(request.conversation_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation_id format"
                )

            # Fetch existing conversation
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = session.exec(statement).first()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=user_id,
                title=_generate_conversation_title(user_message)
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            conversation_id = conversation.id

        # 4. Fetch conversation history (FR-315, FR-316)
        history = _fetch_conversation_history(session, user_id, conversation_id, limit=20)

        # 5. Store user message (FR-312, FR-314)
        user_msg_stored = _store_message(
            session,
            conversation_id,
            user_id,
            "user",
            user_message
        )

        # 6. Call agent (FR-318-FR-326)
        logger.info(f"chat: user={user_id}, conversation={conversation_id}, message={user_message[:50]}")

        try:
            agent = create_agent(user_id)
            agent_result = agent.run(
                messages=_build_message_context(history),
                user_message=user_message
            )
            agent_content = agent_result.get("content", "Sorry, I encountered an error.")
            agent_tool_calls = agent_result.get("tool_calls", [])
        except Exception as e:
            logger.error(f"Agent error: {str(e)}", exc_info=True)
            agent_content = "Sorry, I encountered an error processing your request. Please try again."
            agent_tool_calls = []

        # 7. Store assistant message (FR-313, FR-314)
        tool_calls_json = None
        if agent_tool_calls:
            tool_calls_json = json.dumps({
                "calls": agent_tool_calls
            })

        assistant_msg_stored = _store_message(
            session,
            conversation_id,
            user_id,
            "assistant",
            agent_content,
            tool_calls_json
        )

        # 8. Update conversation updated_at
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        # 9. Return response (FR-307)
        tool_calls_response = [
            ToolCallResult(
                tool_name=call.get("tool_name"),
                input=call.get("input"),
                result=call.get("result")
            )
            for call in agent_tool_calls
        ]

        return ChatResponse(
            id=str(assistant_msg_stored.id),
            conversation_id=str(conversation_id),
            user_id=user_id,
            content=agent_content,
            tool_calls=tool_calls_response,
            created_at=assistant_msg_stored.created_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ===== Conversation Management Endpoints =====

@router.get("/{user_id}/conversations", status_code=status.HTTP_200_OK)
async def list_conversations(
    user_id: str,
    session: Session = Depends(get_session),
    token_user_id: str = Depends(verify_token)
):
    """
    List all conversations for the authenticated user.

    @spec: T-327 (spec.md FR-345, FR-347)
    """
    if token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch"
        )

    try:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        conversations = session.exec(statement).all()

        return {
            "conversations": [
                {
                    "id": str(conv.id),
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ]
        }
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations"
        )


@router.get("/{user_id}/conversations/{conversation_id}", status_code=status.HTTP_200_OK)
async def get_conversation(
    user_id: str,
    conversation_id: str,
    session: Session = Depends(get_session),
    token_user_id: str = Depends(verify_token)
):
    """
    Retrieve full conversation history.

    @spec: T-327 (spec.md FR-346, FR-347)
    """
    if token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch"
        )

    try:
        conv_id = UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation_id format"
        )

    try:
        # Verify user owns conversation
        statement = select(Conversation).where(
            Conversation.id == conv_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Fetch all messages
        message_statement = (
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at.asc())
        )
        messages = session.exec(message_statement).all()

        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "tool_calls": json.loads(msg.tool_calls) if msg.tool_calls else None,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )
