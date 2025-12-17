"""
Chat service for managing sessions and messages.

Handles session lifecycle and integrates with RAG for responses.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatMessage, ChatSession, MessageRoleEnum
from app.schemas.chat import ChatMessage as ChatMessageSchema
from app.schemas.chat import ChatResponse, Source
from app.services.rag_service import RAGService, get_rag_service

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat operations."""

    def __init__(self, db: AsyncSession):
        """Initialize chat service."""
        self.db = db
        self.rag_service: RAGService = get_rag_service()

    async def create_session(
        self,
        user_id: Optional[UUID] = None,
        context_chapter: Optional[str] = None,
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            user_id: Optional user ID (None for anonymous)
            context_chapter: Optional current chapter context

        Returns:
            Created ChatSession
        """
        session = ChatSession(
            user_id=user_id,
            context_chapter=context_chapter,
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)

        logger.info(f"Created chat session: {session.id}")
        return session

    async def get_session(
        self, session_id: UUID, include_messages: bool = True
    ) -> Optional[ChatSession]:
        """
        Get a chat session by ID.

        Args:
            session_id: Session UUID
            include_messages: Whether to load messages

        Returns:
            ChatSession or None if not found
        """
        query = select(ChatSession).where(ChatSession.id == session_id)

        if include_messages:
            query = query.options(selectinload(ChatSession.messages))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_sessions(
        self,
        user_id: UUID,
        limit: int = 10,
        active_only: bool = True,
    ) -> List[ChatSession]:
        """
        Get sessions for a user.

        Args:
            user_id: User UUID
            limit: Maximum number of sessions
            active_only: Only return active sessions

        Returns:
            List of ChatSession
        """
        query = select(ChatSession).where(ChatSession.user_id == user_id)

        if active_only:
            query = query.where(ChatSession.is_active == True)

        query = query.order_by(ChatSession.last_activity.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_message(
        self,
        session_id: UUID,
        role: MessageRoleEnum,
        content: str,
        sources: Optional[List[dict]] = None,
    ) -> ChatMessage:
        """
        Add a message to a session.

        Args:
            session_id: Session UUID
            role: Message role
            content: Message content
            sources: Optional source references

        Returns:
            Created ChatMessage
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)

        return message

    async def process_user_message(
        self,
        session_id: UUID,
        content: str,
    ) -> ChatResponse:
        """
        Process a user message and generate AI response.

        Args:
            session_id: Session UUID
            content: User message content

        Returns:
            ChatResponse with AI response and metadata
        """
        # Get session for context
        session = await self.get_session(session_id, include_messages=False)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Save user message
        await self.add_message(
            session_id=session_id,
            role=MessageRoleEnum.USER,
            content=content,
        )

        # Generate AI response using RAG
        rag_response = self.rag_service.answer_question(
            question=content,
            chapter_context=session.context_chapter,
        )

        # Convert sources to dict for storage
        sources_data = [
            {
                "chapter": s.chapter,
                "section": s.section,
                "url": s.url,
                "relevance_score": s.relevance_score,
                "snippet": s.snippet,
            }
            for s in rag_response.sources
        ]

        # Save assistant message
        assistant_message = await self.add_message(
            session_id=session_id,
            role=MessageRoleEnum.ASSISTANT,
            content=rag_response.answer,
            sources=sources_data,
        )

        # Build response
        return ChatResponse(
            message=ChatMessageSchema(
                id=assistant_message.id,
                role=assistant_message.role,
                content=assistant_message.content,
                sources=[
                    Source(
                        chapter=s["chapter"],
                        section=s["section"],
                        url=s["url"],
                        relevance_score=s["relevance_score"],
                        snippet=s["snippet"],
                    )
                    for s in sources_data
                ],
                created_at=assistant_message.created_at,
            ),
            processingTime=rag_response.processing_time_ms,
            tokensUsed=rag_response.tokens_used,
        )

    async def quick_ask(
        self,
        question: str,
        context_chapter: Optional[str] = None,
    ) -> ChatResponse:
        """
        Answer a question without session (stateless).

        Args:
            question: The question to answer
            context_chapter: Optional chapter context

        Returns:
            ChatResponse with AI response
        """
        # Generate AI response using RAG
        rag_response = self.rag_service.answer_question(
            question=question,
            chapter_context=context_chapter,
        )

        # Build response
        from uuid import uuid4

        return ChatResponse(
            message=ChatMessageSchema(
                id=uuid4(),
                role=MessageRoleEnum.ASSISTANT,
                content=rag_response.answer,
                sources=[
                    Source(
                        chapter=s.chapter,
                        section=s.section,
                        url=s.url,
                        relevance_score=s.relevance_score,
                        snippet=s.snippet,
                    )
                    for s in rag_response.sources
                ],
                created_at=datetime.utcnow(),
            ),
            processingTime=rag_response.processing_time_ms,
            tokensUsed=rag_response.tokens_used,
        )

    async def close_session(self, session_id: UUID) -> bool:
        """
        Close a chat session.

        Args:
            session_id: Session UUID

        Returns:
            True if session was closed
        """
        session = await self.get_session(session_id, include_messages=False)
        if not session:
            return False

        session.is_active = False
        await self.db.flush()

        logger.info(f"Closed chat session: {session_id}")
        return True
