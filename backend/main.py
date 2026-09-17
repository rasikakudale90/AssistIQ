import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.errors import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from backend.api.health import router as health_router
from backend.api.auth import router as auth_router
from backend.api.cases import router as cases_router
from backend.api.messages import router as messages_router
from backend.api.knowledge import router as knowledge_router
from backend.api.search import router as search_router
from backend.api.ai import router as ai_router
from backend.api.sla import router as sla_router
from backend.api.escalations import router as escalations_router
from backend.api.insights import router as insights_router
from backend.api.reports import router as reports_router
from backend.scheduler.scheduler import start_scheduler, stop_scheduler

# Setup structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger("assistiq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup validation
    logger.info("Initializing AssistIQ Backend...")
    settings.validate_startup_config()
    logger.info(f"AssistIQ running in [{settings.ENVIRONMENT}] environment.")

    # Start in-process scheduler (The Sweep) unless disabled for simple tests
    start_scheduler()

    yield
    # Teardown
    logger.info("Shutting down AssistIQ Backend...")
    stop_scheduler()


app = FastAPI(
    title="AssistIQ API",
    description="AI-Assisted IT Helpdesk Backend (FastAPI)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS Middleware with strict origin control
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API v1 routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(sla_router, prefix="/api/v1")
app.include_router(escalations_router, prefix="/api/v1")
app.include_router(insights_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root():
    return {
        "name": "AssistIQ API",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else "disabled",
    }
