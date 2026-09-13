from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.processing import process_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=schemas.DocumentDetail, status_code=status.HTTP_201_CREATED)
def create_document(payload: schemas.DocumentCreate, db: Session = Depends(get_db)):
    document = models.Document(
        title=payload.title.strip(),
        source_type="txt",
        raw_text=payload.text,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[schemas.DocumentListItem])
def list_documents(db: Session = Depends(get_db)):
    return db.query(models.Document).order_by(models.Document.uploaded_at.desc()).all()


@router.get("/{document_id}", response_model=schemas.DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found.",
        )
    return document


@router.post("/{document_id}/process", response_model=schemas.ProcessResult)
def process_document_endpoint(document_id: int, db: Session = Depends(get_db)):
    document = db.get(models.Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found.",
        )

    chunks = process_document(db, document)

    return schemas.ProcessResult(
        document_id=document_id,
        chunk_count=len(chunks),
        chunks=chunks,
    )
