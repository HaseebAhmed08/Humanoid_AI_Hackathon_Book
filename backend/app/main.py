"""
FastAPI application entry point for Physical AI & Humanoid Robotics Platform.

Provides:
- RAG-powered chatbot API
- User authentication endpoints
- Content personalization
- Urdu translation service
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.db.database import close_db, init_db
from app.middleware import LoggingMiddleware, setup_exception_handlers, setup_logging
from app.schemas import HealthResponse

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting Physical AI Platform API v{__version__}")
    logger.info(f"Environment: {settings.environment}")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue without DB in development for frontend work
        if not settings.is_development:
            raise

    yield

    # Shutdown
    logger.info("Shutting down Physical AI Platform API")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Physical AI & Humanoid Robotics Platform API",
    description="Backend API for the educational platform covering ROS 2, simulation, and AI integration.",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Setup exception handlers
setup_exception_handlers(app)

# Add CORS middleware
# Allow all origins for flexibility with Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)


# =============================================================================
# Health Check Endpoints
# =============================================================================


@app.get("/", tags=["health"])
async def root():
    """Root endpoint - basic health check."""
    return {
        "name": "Physical AI & Humanoid Robotics Platform API",
        "version": __version__,
        "status": "running",
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Detailed health check endpoint.

    Returns status of the API and dependent services.
    """
    services = {}

    # Check database
    try:
        from app.db.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        services["database"] = "healthy"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        services["database"] = "unhealthy"

    # Check Qdrant (if configured)
    if settings.qdrant_url:
        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )
            client.get_collections()
            services["qdrant"] = "healthy"
        except Exception as e:
            logger.warning(f"Qdrant health check failed: {e}")
            services["qdrant"] = "unhealthy"

    # Determine overall status
    all_healthy = all(s == "healthy" for s in services.values())
    status = "healthy" if all_healthy else "degraded"

    return HealthResponse(
        status=status,
        version=__version__,
        environment=settings.environment,
        services=services,
    )


# =============================================================================
# API Routers
# =============================================================================

from app.routers import chat_router

# Chat API (RAG-powered Q&A)
app.include_router(chat_router, prefix="/api")

# Uncomment as routers are created:
# from app.routers import auth, profile, translate
# app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
# app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
# app.include_router(translate.router, prefix="/api/translate", tags=["translation"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )
