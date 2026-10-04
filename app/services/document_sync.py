from sqlalchemy.orm import Session

from app.core import config
from app.models import models


def sync_documents_from_disk(db: Session) -> None:
    """Make every readable text file in the docs folder (config.DOCS_DIR) exist
    as exactly one Document row, with raw_text kept in sync with the file's
    current contents. Documents with no matching file are removed along with
    their chunks. The file on disk is the source of truth, not the database.

    Any file dropped in the folder becomes a Document automatically — nothing
    about a specific file is hardcoded."""
    docs_dir = config.DOCS_DIR
    if not docs_dir.exists():
        return

    synced_titles: set[str] = set()

    for path in sorted(docs_dir.iterdir()):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not text.strip():
            continue

        synced_titles.add(path.name)
        document = db.query(models.Document).filter(models.Document.title == path.name).one_or_none()

        if document is None:
            db.add(
                models.Document(
                    title=path.name,
                    source_type=path.suffix.lstrip(".") or "txt",
                    raw_text=text,
                )
            )
        elif document.raw_text != text:
            document.raw_text = text
            document.chunks.clear()

    stale = db.query(models.Document).filter(~models.Document.title.in_(synced_titles)).all()
    for document in stale:
        db.delete(document)

    db.commit()
