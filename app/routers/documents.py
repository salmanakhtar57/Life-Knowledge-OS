from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.processing import sync_knowledge_base

# Owner-only: these expose the raw notes and trigger paid embedding calls.
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[schemas.DocumentListItem])
def list_documents(db: Session = Depends(get_db)):
    return db.query(models.Document).order_by(models.Document.uploaded_at.desc()).all()


@router.post("/sync", response_model=schemas.SyncResult)
def sync_documents(db: Session = Depends(get_db)):
    """Re-read the docs folder and chunk + embed anything new or changed."""
    sync_knowledge_base(db)
    return schemas.SyncResult(
        document_count=db.query(models.Document).count(),
        chunk_count=db.query(models.Chunk).count(),
    )


@router.get("/{document_id}", response_model=schemas.DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found.",
        )
    return document
