"""Pull posts from an external source into the same documents table the docs
folder uses. Posts then go through the existing chunk + embed pipeline, so
nothing downstream (search, /ask) needs to know where a document came from."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import config
from app.models import models
from app.services.feeds import fetch_feed_articles, normalize_substack_feed_url
from app.services.processing import process_pending_documents


@dataclass
class SyncResult:
    fetched: int
    new: int
    skipped_duplicates: int
    skipped_empty: int


def _get_or_create_source(
    db: Session, platform: models.SourcePlatform, url: str
) -> models.Source:
    source = db.query(models.Source).filter(models.Source.url == url).one_or_none()
    if source is not None:
        return source
    try:
        with db.begin_nested():
            source = models.Source(platform=platform, url=url)
            db.add(source)
    except IntegrityError:
        # A concurrent sync created it first.
        source = db.query(models.Source).filter(models.Source.url == url).one()
    return source


def _sync_feed(db: Session, platform: models.SourcePlatform, feed_url: str) -> SyncResult:
    # Network first, before any database work, so a bad feed changes nothing.
    articles = fetch_feed_articles(feed_url)

    source = _get_or_create_source(db, platform, feed_url)

    urls = [a.url for a in articles]
    known = {
        url
        for (url,) in db.query(models.Document.url).filter(models.Document.url.in_(urls))
    }

    new = duplicates = empty = 0
    for article in articles:
        if article.url in known:
            duplicates += 1
            continue
        if len(article.text) < config.MIN_ARTICLE_CHARS:
            empty += 1
            continue
        try:
            with db.begin_nested():
                db.add(
                    models.Document(
                        source_id=source.id,
                        url=article.url,
                        title=article.title,
                        published_at=article.published_at,
                        raw_text=article.text,
                    )
                )
        except IntegrityError:
            duplicates += 1
            continue
        known.add(article.url)
        new += 1

    source.last_synced_at = func.now()
    db.commit()

    # Chunk + embed anything that has no chunks yet. This also retries posts
    # saved by an earlier sync whose embedding call failed.
    process_pending_documents(db)

    return SyncResult(
        fetched=len(articles),
        new=new,
        skipped_duplicates=duplicates,
        skipped_empty=empty,
    )


def sync_substack(db: Session, publication_url: str) -> SyncResult:
    feed_url = normalize_substack_feed_url(publication_url)
    return _sync_feed(db, models.SourcePlatform.SUBSTACK, feed_url)