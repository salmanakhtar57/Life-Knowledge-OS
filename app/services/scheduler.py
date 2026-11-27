import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.core import config
from app.database.database import SessionLocal
from app.services.source_sync import sync_substack

logger = logging.getLogger(__name__)

scheduler: BackgroundScheduler | None = None


def scheduled_substack_sync() -> None:
    """Scheduled task that syncs Substack using its own database session."""

    db: Session = SessionLocal()

    try:
        result = sync_substack(db)

        if result.get("already_running"):
            logger.info("Substack sync skipped: another sync is running.")
            return

        logger.info("Scheduled Substack sync completed: %s", result)

    except Exception:
        logger.exception("Scheduled Substack sync failed.")

    finally:
        db.close()


def start_scheduler() -> None:
    """Start the daily Substack scheduler."""

    global scheduler

    if scheduler is not None and scheduler.running:
        return

    scheduler = BackgroundScheduler(timezone="UTC")

    scheduler.add_job(
        scheduled_substack_sync,
        trigger="interval",
        hours=config.SUBSTACK_SYNC_INTERVAL_HOURS,
        id="substack_daily_sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()

    logger.info(
        "Substack scheduler started. Interval: %s hours",
        config.SUBSTACK_SYNC_INTERVAL_HOURS,
    )


def stop_scheduler() -> None:
    """Stop the scheduler gracefully."""

    global scheduler

    if scheduler is not None and scheduler.running:
        scheduler.shutdown(wait=False)
        scheduler = None