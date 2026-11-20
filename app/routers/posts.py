from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.source_sync import sync_substack

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    # dependencies=[Depends(get_current_user)],
)


def _substack_query(db: Session):
    return (
        db.query(models.Document)
        .join(models.Source)
        .filter(models.Source.platform == models.SourcePlatform.SUBSTACK)
    )


@router.get("/latest", response_model=list[schemas.PostOut])
def get_latest_posts(db: Session = Depends(get_db)):
    return (
        _substack_query(db)
        .order_by(models.Document.published_at.desc().nullslast())
        .limit(3)
        .all()
    )


@router.get("", response_model=list[schemas.PostOut])
def get_all_posts(db: Session = Depends(get_db)):
    return (
        _substack_query(db)
        .order_by(models.Document.published_at.desc().nullslast())
        .all()
    )


@router.post("/sync", response_model=schemas.PostSyncResponse)
def sync_posts(db: Session = Depends(get_db)):
    return sync_substack(db)