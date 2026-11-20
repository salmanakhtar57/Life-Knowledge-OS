from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas import schemas
from app.services import source_sync
from app.services.feeds import FeedError

router = APIRouter(prefix="/sources", tags=["sources"])

# NOTE: if your document routes use an auth dependency (e.g. dependencies=[Depends(...)]
# on the router), add the same one here so this endpoint is protected too.


@router.post("/substack/sync", response_model=schemas.SyncResult)
def sync_substack(payload: schemas.SubstackSyncRequest, db: Session = Depends(get_db)):
    """Fetch a Substack publication's feed and store any posts not seen before.
    Safe to call repeatedly: known posts are skipped, never duplicated."""
    try:
        result = source_sync.sync_substack(db, payload.url)
    except FeedError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return schemas.SyncResult(
        fetched=result.fetched,
        new=result.new,
        skipped_duplicates=result.skipped_duplicates,
        skipped_empty=result.skipped_empty,
    )