import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core import config
from app.services.openrouter_client import AIServiceError
from app.core.routing import api_router
from app.database.database import SessionLocal, init_db
from app.services.processing import sync_knowledge_base

logger = logging.getLogger(__name__)


def _startup_sync() -> None:
    init_db()
    db = SessionLocal()
    try:
        sync_knowledge_base(db)
    except AIServiceError:
        # Start anyway: questions still work against what's already embedded,
        # and POST /documents/sync can retry later.
        logger.exception("Startup sync failed; serving existing data")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await run_in_threadpool(_startup_sync)
    yield


app = FastAPI(title="Life Knowledge OS", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=config.CORS_ORIGIN_REGEX,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AIServiceError)
async def handle_ai_service_error(_request: Request, exc: AIServiceError):
    # Full details stay in the server log; the client only gets a generic message.
    logger.error("AI service error: %s", exc, exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "The AI service is unavailable right now. Please try again in a moment."},
    )


app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
