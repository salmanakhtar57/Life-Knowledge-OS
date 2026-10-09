import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core import config
from app.core.security import get_current_user
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.document_sync import file_url, sync_documents_from_disk
from app.services.openrouter_client import AIServiceError
from app.services.processing import sync_knowledge_base

router = APIRouter(prefix="/documents", tags=["documents"])

# Listing, reading and syncing are owner-only: they expose the raw notes and
# trigger embedding calls for the whole folder. Upload is public.
owner_only = [Depends(get_current_user)]


@router.get("", response_model=list[schemas.DocumentListItem], dependencies=owner_only)
def list_documents(db: Session = Depends(get_db)):
    return db.query(models.Document).order_by(models.Document.created_at.desc()).all()


@router.post("/sync", response_model=schemas.SyncResult, dependencies=owner_only)
def sync_documents(db: Session = Depends(get_db)):
    """Re-read the docs folder and chunk + embed anything new or changed."""
    sync_knowledge_base(db)
    return schemas.SyncResult(
        document_count=db.query(models.Document).count(),
        chunk_count=db.query(models.Chunk).count(),
    )


_SAFE_FILENAME = re.compile(r"^[\w\- .]+$")


@router.post("/upload", response_model=schemas.UploadResult, status_code=status.HTTP_201_CREATED)
def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    """Save an uploaded text file into the docs folder, then sync. The result is
    the same as dropping the file into the folder by hand: it is chunked and
    embedded by the normal pipeline, and the folder stays the source of truth."""
    filename = Path(file.filename or "").name
    if (
        not _SAFE_FILENAME.match(filename)
        or filename.startswith(".")
        or Path(filename).suffix.lower() not in config.UPLOAD_ALLOWED_EXTENSIONS
    ):
        allowed = ", ".join(sorted(config.UPLOAD_ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload a text file ({allowed}) with a simple file name.",
        )

    content = file.file.read(config.UPLOAD_MAX_BYTES + 1)
    if len(content) > config.UPLOAD_MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File is larger than {config.UPLOAD_MAX_BYTES // 1024} KB.",
        )
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be UTF-8 text."
        )
    if not text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty.")

    path = config.DOCS_DIR / filename
    if path.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A document named {filename} already exists.",
        )

    config.DOCS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    try:
        sync_knowledge_base(db)
    except AIServiceError:
        # Embedding failed: remove the file and its row so the upload can simply be retried.
        db.rollback()
        path.unlink(missing_ok=True)
        sync_documents_from_disk(db)
        raise

    document = db.query(models.Document).filter(models.Document.url == file_url(filename)).one()
    return schemas.UploadResult(
        id=document.id,
        title=document.title,
        chunk_count=db.query(models.Chunk).filter(models.Chunk.document_id == document.id).count(),
    )


@router.get("/{document_id}", response_model=schemas.DocumentDetail, dependencies=owner_only)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found.",
        )
    return document
