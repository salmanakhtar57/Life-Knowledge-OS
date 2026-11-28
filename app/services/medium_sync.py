
from datetime import datetime, timezone
import logging
import threading

from sqlalchemy.orm import Session

from app.core import config
from app.models import models
from app.services.feeds import (
    fetch_medium_posts,
    normalize_medium_url,
)
from app.services.processing import process_pending_documents
from app.services.writing_ideas import refresh_medium_writing_ideas

logger = logging.getLogger(__name__)

_medium_sync_lock = threading.Lock()


def get_or_create_medium_source(db: Session) -> models.Source:
    """Register the Medium profile if it does not already exist."""

    profile_url = normalize_medium_url(config.MEDIUM_URL)

    source = (
        db.query(models.Source)
        .filter(models.Source.url == profile_url)
        .one_or_none()
    )

    if source is None:
        source = models.Source(
            platform=models.SourcePlatform.MEDIUM,
            url=profile_url,
        )
        db.add(source)
        db.flush()

    return source


def _sync_medium(db: Session) -> dict:
    """Fetch Medium articles and store new ones."""

    if not config.MEDIUM_URL:
        return {
            "fetched": 0,
            "new": 0,
            "skipped_duplicates": 0,
            "skipped_empty": 0,
            "message": "Medium URL is not configured.",
        }

    source = get_or_create_medium_source(db)
    posts = fetch_medium_posts()

    fetched = len(posts)
    new_count = 0
    skipped_duplicates = 0
    skipped_empty = 0

    for post in posts:
        existing = (
            db.query(models.Document)
            .filter(models.Document.url == post["url"])
            .one_or_none()
        )

        if existing is not None:
            skipped_duplicates += 1
            continue

        if len(post["raw_text"]) < config.MIN_ARTICLE_CHARS:
            skipped_empty += 1
            continue

        document = models.Document(
            source_id=source.id,
            url=post["url"],
            title=post["title"],
            published_at=post["published_at"],
            raw_text=post["raw_text"],
        )

        db.add(document)
        new_count += 1

    source.last_synced_at = datetime.now(timezone.utc)

    db.commit()

    process_pending_documents(db)

    if new_count > 0:
        try:
            refresh_medium_writing_ideas(db)
            logger.info(
                "Medium writing suggestions regenerated after adding %s new article(s).",
                new_count,
            )
        except Exception:
            logger.exception(
                "New Medium articles were saved, but writing suggestions "
                "could not be regenerated."
            )

    return {
        "fetched": fetched,
        "new": new_count,
        "skipped_duplicates": skipped_duplicates,
        "skipped_empty": skipped_empty,
        "message": (
            "Medium is up to date."
            if new_count == 0
            else f"Added {new_count} new Medium article(s)."
        ),
    }


def sync_medium(db: Session) -> dict:
    """Run Medium synchronization with a concurrency lock."""

    if not _medium_sync_lock.acquire(blocking=False):
        return {
            "fetched": 0,
            "new": 0,
            "skipped_duplicates": 0,
            "skipped_empty": 0,
            "message": "A Medium synchronization is already running.",
            "already_running": True,
        }

    try:
        return _sync_medium(db)

    finally:
        _medium_sync_lock.release()
