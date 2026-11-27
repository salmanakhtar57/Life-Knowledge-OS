from datetime import datetime, timezone
import logging
import threading

from sqlalchemy.orm import Session

from app.core import config
from app.models import models
from app.services.feeds import fetch_substack_posts, normalize_substack_url
from app.services.processing import process_pending_documents
from app.services.writing_ideas import refresh_substack_writing_ideas

logger = logging.getLogger(__name__)

_sync_lock = threading.Lock()


def get_or_create_substack_source(
    db: Session,
) -> models.Source:
    """Register the configured Substack publication if necessary."""

    publication_url = normalize_substack_url(config.SUBSTACK_URL)

    source = (
        db.query(models.Source)
        .filter(models.Source.url == publication_url)
        .one_or_none()
    )

    if source is None:
        source = models.Source(
            platform=models.SourcePlatform.SUBSTACK,
            url=publication_url,
        )
        db.add(source)
        db.flush()

    return source


def _sync_substack(db: Session) -> dict:
    """Fetch available Substack articles and store new ones.

    Existing posts are identified by URL and are not updated.
    """

    if not config.SUBSTACK_URL:
        return {
            "fetched": 0,
            "new": 0,
            "skipped_duplicates": 0,
            "skipped_empty": 0,
            "message": "Substack URL is not configured.",
        }

    source = get_or_create_substack_source(db)

    posts = fetch_substack_posts(config.SUBSTACK_URL)

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

    # Save fetched articles before embedding.
    # If the AI provider fails, the articles are still stored.
    source.last_synced_at = datetime.now(timezone.utc)

    db.commit()

    # Embed documents which don't have chunks yet.
    # This also handles documents left pending by a previous failed sync.
    process_pending_documents(db)

    # Regenerate writing suggestions only when new articles were added.
    if new_count > 0:
        try:
            refresh_substack_writing_ideas(db)
            logger.info(
                "Writing suggestions regenerated after adding %s new article(s).",
                new_count,
            )
        except Exception:
            logger.exception(
                "New Substack articles were saved, but writing suggestions "
                "could not be regenerated."
            )

    return {
        "fetched": fetched,
        "new": new_count,
        "skipped_duplicates": skipped_duplicates,
        "skipped_empty": skipped_empty,
        "message": (
            "Substack is up to date."
            if new_count == 0
            else f"Added {new_count} new article(s)."
        ),
    }


def sync_substack(db: Session) -> dict:
    """Run Substack synchronization only if another sync isn't active."""

    if not _sync_lock.acquire(blocking=False):
        return {
            "fetched": 0,
            "new": 0,
            "skipped_duplicates": 0,
            "skipped_empty": 0,
            "message": "A synchronization is already running.",
            "already_running": True,
        }

    try:
        return _sync_substack(db)
    finally:
        _sync_lock.release()