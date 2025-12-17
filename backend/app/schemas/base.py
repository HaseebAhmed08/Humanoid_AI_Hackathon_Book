"""
Base Pydantic schemas for common response models.

Provides standard response wrappers for API endpoints.
"""

from datetime import datetime
from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel, Field

# Generic type for paginated data
T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response model with success flag and message."""

    success: bool = Field(default=True, description="Whether the request succeeded")
    message: str | None = Field(default=None, description="Optional message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp",
    )


class ErrorResponse(BaseModel):
    """Error response model with details."""

    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(description="Error type or code")
    message: str = Field(description="Human-readable error message")
    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional error details",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp",
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper for list endpoints."""

    success: bool = Field(default=True)
    data: List[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_prev: bool = Field(description="Whether there are previous pages")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(description="Health status: healthy, degraded, unhealthy")
    version: str = Field(description="API version")
    environment: str = Field(description="Environment name")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Check timestamp",
    )
    services: dict[str, str] = Field(
        default_factory=dict,
        description="Status of dependent services",
    )


class DataResponse(BaseModel, Generic[T]):
    """Generic data response wrapper."""

    success: bool = Field(default=True)
    data: T = Field(description="Response data")
    message: str | None = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
