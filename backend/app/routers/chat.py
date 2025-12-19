"""
Chat API router.

Provides endpoints for chat sessions and RAG-powered Q&A.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.error_handler import NotFoundError
from app.schemas.chat import (
    ChatResponse,
    ChatSession,
    ChatSessionWithMessages,
    CreateSessionRequest,
    QuickQuestionRequest,
    SendMessageRequest,
)
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


async def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Dependency to get chat service."""
    return ChatService(db)


@router.post(
    "/sessions",
    response_model=ChatSession,
    status_code=status.HTTP_201_CREATED,
    summary="Create new chat session",
)
async def create_session(
    request: CreateSessionRequest,
    service: ChatService = Depends(get_chat_service),
):
    """
    Create a new chat session.

    Sessions can be anonymous or linked to a user. Provide optional
    chapter context for more relevant responses.
    """
    session = await service.create_session(
        context_chapter=request.context_chapter,
    )
    return session


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionWithMessages,
    summary="Get chat session with messages",
)
async def get_session(
    session_id: UUID,
    service: ChatService = Depends(get_chat_service),
):
    """
    Get a chat session by ID including message history.
    """
    session = await service.get_session(session_id, include_messages=True)
    if not session:
        raise NotFoundError("Chat session", str(session_id))

    # Convert to response model
    from app.schemas.chat import ChatMessage as ChatMessageSchema
    from app.schemas.chat import Source

    messages = []
    for msg in session.messages:
        sources = None
        if msg.sources:
            sources = [
                Source(
                    chapter=s["chapter"],
                    section=s["section"],
                    url=s["url"],
                    relevance_score=s["relevance_score"],
                    snippet=s["snippet"],
                )
                for s in msg.sources
            ]
        messages.append(
            ChatMessageSchema(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                sources=sources,
                created_at=msg.created_at,
            )
        )

    return ChatSessionWithMessages(
        id=session.id,
        user_id=session.user_id,
        started_at=session.started_at,
        context_chapter=session.context_chapter,
        is_active=session.is_active,
        messages=messages,
    )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatResponse,
    summary="Send message and get AI response",
)
async def send_message(
    session_id: UUID,
    request: SendMessageRequest,
    service: ChatService = Depends(get_chat_service),
):
    """
    Send a message to a chat session and receive an AI response.

    The AI will use RAG to find relevant content from the textbook
    and provide an informed answer with source citations.
    """
    try:
        response = await service.process_user_message(
            session_id=session_id,
            content=request.content,
        )
        return response
    except ValueError as e:
        logger.error(f"Session not found: {session_id}")
        raise NotFoundError("Chat session", str(session_id))
    except Exception as e:
        logger.exception(f"Error processing message for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="Quick question (stateless)",
)
async def ask_question(
    request: QuickQuestionRequest,
    service: ChatService = Depends(get_chat_service),
):
    """
    Ask a question without creating a session.

    This is a stateless endpoint for quick queries. For conversation
    history and context, use the session-based endpoints instead.
    """
    try:
        logger.info(f"Quick ask received: {request.question[:50]}...")
        response = await service.quick_ask(
            question=request.question,
            context_chapter=request.context_chapter,
        )
        return response
    except Exception as e:
        logger.exception(f"Error processing quick question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Close a chat session",
)
async def close_session(
    session_id: UUID,
    service: ChatService = Depends(get_chat_service),
):
    """
    Close a chat session.

    Closed sessions are marked inactive but not deleted.
    """
    success = await service.close_session(session_id)
    if not success:
        raise NotFoundError("Chat session", str(session_id))
