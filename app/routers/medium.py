
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import models
from app.schemas.schemas import PostOut, PostSyncResponse
from app.services.medium_sync import sync_medium

router = APIRouter(prefix="/medium", tags=["medium"])


def _medium_query(db: Session):
    return (
        db.query(models.Document)
        .join(models.Source)
        .filter(models.Source.platform == models.SourcePlatform.MEDIUM)
    )


@router.get("/posts", response_model=list[PostOut])
def get_medium_posts(db: Session = Depends(get_db)):
    """Return all locally stored Medium posts."""

    return (
        _medium_query(db)
        .order_by(models.Document.published_at.desc().nullslast())
        .all()
    )


@router.get("/posts/latest", response_model=list[PostOut])
def get_latest_medium_posts(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Return the latest locally stored Medium posts."""

    return (
        _medium_query(db)
        .order_by(models.Document.published_at.desc().nullslast())
        .limit(limit)
        .all()
    )


@router.post("/sync", response_model=PostSyncResponse)
def sync_medium_posts(db: Session = Depends(get_db)):
    """Fetch and store new Medium posts."""

    return sync_medium(db)
