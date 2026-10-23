from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.helpers.exception_handlers import register_exception_handlers
from app.api.helpers.middleware import LoggingMiddleware
from app.api.router import router
from app.config import settings
from app.config.logging_config import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Application starting up")
    yield
    # Shutdown
    logger.info("Application shutting down")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(LoggingMiddleware)

# Register exception handlers
register_exception_handlers(app)

# Include API routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server")
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )