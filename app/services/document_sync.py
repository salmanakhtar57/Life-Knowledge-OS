from pathlib import Path

from sqlalchemy.orm import Session

from app.models import models

# The folder documents are read from. Any file dropped in here becomes a
# Document automatically — nothing about a specific file is hardcoded.
DOCS_DIR = Path(__file__).resolve().parents[2] / "FAQs"


def sync_documents_from_disk(db: Session) -> None:
    """Make every readable text file in DOCS_DIR exist as a Document row,
    with raw_text kept in sync with the file's current contents. The file
    on disk is the source of truth, not the database."""
    if not DOCS_DIR.exists():
        return

    for path in sorted(DOCS_DIR.iterdir()):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not text.strip():
            continue

        document = db.query(models.Document).filter(models.Document.title == path.name).first()
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
            db.query(models.Chunk).filter(models.Chunk.document_id == document.id).delete()

    db.commit()
