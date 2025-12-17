"""
Logging configuration and middleware for FastAPI.

Provides structured logging with request/response tracking.
"""

import logging
import sys
import time
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()

    # Determine log level based on environment
    log_level = logging.DEBUG if settings.is_development else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Set specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.is_development else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {settings.environment} environment")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        # Generate request ID
        request_id = str(uuid4())[:8]
        request.state.request_id = request_id

        # Start timer
        start_time = time.perf_counter()

        # Get logger
        logger = logging.getLogger("app.http")

        # Log request
        logger.info(
            f"[{request_id}] --> {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client": request.client.host if request.client else "unknown",
            },
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception
            duration = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"[{request_id}] <-- {request.method} {request.url.path} "
                f"500 ERROR ({duration:.2f}ms)",
                extra={
                    "request_id": request_id,
                    "duration_ms": duration,
                    "error": str(e),
                },
            )
            raise

        # Calculate duration
        duration = (time.perf_counter() - start_time) * 1000

        # Log response
        log_level = logging.INFO if response.status_code < 400 else logging.WARNING
        logger.log(
            log_level,
            f"[{request_id}] <-- {request.method} {request.url.path} "
            f"{response.status_code} ({duration:.2f}ms)",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration_ms": duration,
            },
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
