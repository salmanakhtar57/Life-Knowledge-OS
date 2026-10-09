from sqlalchemy.orm import Session

from app.core import config
from app.models import models

# The docs folder is stored as one Source row; its files get "file:<name>" URLs.
PERSONAL_SOURCE_URL = "file:docs-folder"


def file_url(filename: str) -> str:
    return f"file:{filename}"


def get_personal_source(db: Session) -> models.Source:
    source = (
        db.query(models.Source).filter(models.Source.url == PERSONAL_SOURCE_URL).one_or_none()
    )
    if source is None:
        source = models.Source(platform=models.SourcePlatform.PERSONAL, url=PERSONAL_SOURCE_URL)
        db.add(source)
        db.flush()
    return source


def sync_documents_from_disk(db: Session) -> None:
    """Make every readable text file in the docs folder (config.DOCS_DIR) exist
    as exactly one Document row, with raw_text kept in sync with the file's
    current contents. Documents with no matching file are removed along with
    their chunks. The file on disk is the source of truth, not the database.

    Only the docs folder's own documents are touched; documents from other
    sources (Substack, Medium, ...) are never removed here.

    Any file dropped in the folder becomes a Document automatically — nothing
    about a specific file is hardcoded."""
    docs_dir = config.DOCS_DIR
    if not docs_dir.exists():
        return

    source = get_personal_source(db)
    synced_urls: set[str] = set()

    for path in sorted(docs_dir.iterdir()):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not text.strip():
            continue

        url = file_url(path.name)
        synced_urls.add(url)
        document = db.query(models.Document).filter(models.Document.url == url).one_or_none()

        if document is None:
            db.add(models.Document(source_id=source.id, url=url, title=path.name, raw_text=text))
        elif document.raw_text != text:
            document.raw_text = text
            document.chunks.clear()

    stale = (
        db.query(models.Document)
        .filter(models.Document.source_id == source.id, ~models.Document.url.in_(synced_urls))
        .all()
    )
    for document in stale:
        db.delete(document)

    db.commit()
