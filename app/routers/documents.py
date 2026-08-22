import io
import json
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import ValidationError
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from sqlalchemy.orm import Session

from app.schemas import schemas
from app.database.database import get_db
from app.models import models

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".txt", ".md", ".json", ".csv", ".html", ".htm", ".rtf", ".log", ".pdf"}


def _save(db: Session, title: str, source_type: str, raw_text: str) -> models.Document:
    document = models.Document(title=title, source_type=source_type, raw_text=raw_text)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.post("", response_model=schemas.DocumentDetail, status_code=status.HTTP_201_CREATED)
async def create_document(
    request: Request,
    db: Session = Depends(get_db),
    file: Optional[UploadFile] = File(None),
):
    """Accepts EITHER a multipart/form-data upload with a 'file' field
    (.txt/.md/.json/.csv/.html/.htm/.rtf/.log as UTF-8 text, or .pdf with text extracted via pypdf),
    OR an application/json body: {"title": str, "text": str}.
    The OpenAPI schema below reflects the file-upload form; use raw JSON for the other case."""
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("multipart/form-data"):
        if file is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided in multipart request.",
            )

        filename = file.filename or ""
        ext = filename[filename.rfind(".") :].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{ext or 'unknown'}'. Accepted types: {allowed}.",
            )

        raw_bytes = await file.read()

        if ext == ".pdf":
            try:
                reader = PdfReader(io.BytesIO(raw_bytes))
            except (PdfReadError, ValueError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not read PDF file: {exc}",
                )
            text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
            if not text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No extractable text found in PDF (it may be scanned/image-only).",
                )
        else:
            try:
                text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File must be UTF-8 encoded text.",
                )
            if not text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uploaded file is empty.",
                )

        return _save(db, title=filename, source_type=ext.lstrip("."), raw_text=text)

    if content_type.startswith("application/json"):
        body = await request.json()
        try:
            payload = schemas.DocumentCreate.model_validate(body)
        except ValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=json.loads(exc.json()),
            )

        return _save(db, title=payload.title.strip(), source_type="txt", raw_text=payload.text)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Send either multipart/form-data with a 'file' field, or an application/json body with 'title' and 'text'.",
    )


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
