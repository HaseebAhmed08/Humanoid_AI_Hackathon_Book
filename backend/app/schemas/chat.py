"""
Pydantic schemas for chat API.

Defines request/response models per contracts/chat.yaml.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Chat message role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Source(BaseModel):
    """Source reference for RAG responses."""

    chapter: str = Field(description="Chapter title")
    section: str = Field(description="Section heading")
    url: str = Field(description="Direct link to source")
    relevance_score: float = Field(
        ge=0, le=1, description="Relevance score (0-1)"
    )
    snippet: str = Field(max_length=500, description="Text excerpt")

    class Config:
        json_schema_extra = {
            "example": {
                "chapter": "Understanding Nodes and Topics",
                "section": "Node Lifecycle",
                "url": "/docs/module-1-ros/nodes-topics#lifecycle",
                "relevance_score": 0.89,
                "snippet": "ROS 2 nodes have a defined lifecycle that controls their state..."
            }
        }


class ChatMessage(BaseModel):
    """A single chat message."""

    id: UUID
    role: MessageRole
    content: str
    sources: Optional[List[Source]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSession(BaseModel):
    """Chat session metadata."""

    id: UUID
    user_id: Optional[UUID] = None
    started_at: datetime
    context_chapter: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSession):
    """Chat session with message history."""

    messages: List[ChatMessage] = Field(default_factory=list)


# Request schemas
class CreateSessionRequest(BaseModel):
    """Request to create a new chat session."""

    context_chapter: Optional[str] = Field(
        None,
        alias="contextChapter",
        description="Current chapter path for context",
        example="/docs/module-1-ros/nodes-topics",
    )


class SendMessageRequest(BaseModel):
    """Request to send a message in a session."""

    content: str = Field(
        min_length=1,
        max_length=2000,
        description="Message content",
        example="What is a ROS 2 node?",
    )


class QuickQuestionRequest(BaseModel):
    """Request for stateless quick question."""

    question: str = Field(
        min_length=1,
        max_length=2000,
        description="The question to ask",
    )
    context_chapter: Optional[str] = Field(
        None,
        alias="contextChapter",
        description="Optional chapter context",
    )


# Response schemas
class ChatResponse(BaseModel):
    """Response from chat API."""

    message: ChatMessage
    processing_time: float = Field(
        alias="processingTime",
        description="Response time in milliseconds",
    )
    tokens_used: int = Field(
        alias="tokensUsed",
        description="Total tokens consumed",
    )

    class Config:
        populate_by_name = True
