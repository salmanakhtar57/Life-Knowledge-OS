import json

from sqlalchemy.orm import Session

from app.models import models
from app.services.chunking import chunk_text
from app.services.embeddings import embed_text


def process_document(db: Session, document: models.Document) -> list[models.Chunk]:
    """Chunk + embed a document's raw_text, replacing any existing chunks. Idempotent."""
    db.query(models.Chunk).filter(models.Chunk.document_id == document.id).delete()

    pieces = chunk_text(document.raw_text)
    chunks = [
        models.Chunk(
            document_id=document.id,
            chunk_index=i,
            text=piece,
            embedding=json.dumps(embed_text(piece)),
        )
        for i, piece in enumerate(pieces)
    ]
    db.add_all(chunks)
    db.commit()
    for chunk in chunks:
        db.refresh(chunk)
    return chunks


def ensure_all_documents_processed(db: Session) -> None:
    """Chunk + embed any document that doesn't have chunks yet. Already-processed
    documents are left untouched (no repeat embedding calls)."""
    processed_ids = {row[0] for row in db.query(models.Chunk.document_id).distinct()}
    unprocessed = db.query(models.Document).filter(~models.Document.id.in_(processed_ids)).all()
    for document in unprocessed:
        process_document(db, document)
