from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    # dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    substack_source = (
        db.query(models.Source)
        .filter(models.Source.platform == models.SourcePlatform.SUBSTACK)
        .one_or_none()
    )

    substack_count = 0
    last_published_at = None
    last_synced_at = None

    if substack_source:
        substack_count = (
            db.query(func.count(models.Document.id))
            .filter(models.Document.source_id == substack_source.id)
            .scalar()
        )

        last_published_at = (
            db.query(func.max(models.Document.published_at))
            .filter(models.Document.source_id == substack_source.id)
            .scalar()
        )

        last_synced_at = substack_source.last_synced_at

    medium_count = (
        db.query(func.count(models.Document.id))
        .join(models.Source)
        .filter(models.Source.platform == models.SourcePlatform.MEDIUM)
        .scalar()
    )
    
    faq_count = (
        db.query(func.count(models.Document.id))
        .join(models.Source)
        .filter(models.Source.platform == models.SourcePlatform.PERSONAL)
        .scalar()
    )

    days_since_last_post = None

    if last_published_at:
        now = datetime.now(timezone.utc)

        if last_published_at.tzinfo is None:
            last_published_at = last_published_at.replace(
                tzinfo=timezone.utc
            )

        days_since_last_post = (now - last_published_at).days

    return schemas.StatsResponse(
        substack_posts=substack_count or 0,
        faq_documents=faq_count or 0,
        last_published_at=last_published_at,
        days_since_last_post=days_since_last_post,
        last_synced_at=last_synced_at,
        medium_posts=medium_count or 0,
    )