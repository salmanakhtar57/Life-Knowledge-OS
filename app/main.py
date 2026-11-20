import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core import config
from app.core.routing import api_router
from app.database.database import SessionLocal, init_db
from app.services.openrouter_client import AIServiceError
from app.services.processing import sync_knowledge_base
from app.services.scheduler import (
scheduled_substack_sync,
    start_scheduler,
    stop_scheduler,
)

logger = logging.getLogger(__name__)


def _startup_sync() -> None:
    """Initialize the database and synchronize existing FAQ documents."""

    init_db()

    db = SessionLocal()

    try:
        sync_knowledge_base(db)

    except AIServiceError:
        logger.exception(
            "FAQ knowledge-base synchronization failed. "
            "Starting with existing data."
        )

    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Initialize the DB and process local FAQs.
    await run_in_threadpool(_startup_sync)

    # Fetch Substack content at startup.
    await run_in_threadpool(scheduled_substack_sync)

    # Start the daily scheduler.
    start_scheduler()

    yield

    # Stop the scheduler during application shutdown.
    stop_scheduler()


app = FastAPI(
    title="Noteway",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=config.CORS_ORIGIN_REGEX,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AIServiceError)
async def handle_ai_service_error(
    _request: Request,
    exc: AIServiceError,
):
    logger.error(
        "AI service error: %s",
        exc,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": (
                "The AI service is unavailable right now. "
                "Please try again in a moment."
            )
        },
    )


app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)