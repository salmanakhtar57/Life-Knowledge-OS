import json
import threading

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core import config
from app.models import models
from app.services.chunking import chunk_text
from app.services.document_sync import sync_documents_from_disk
from app.services.embeddings import embed_texts

# Serializes syncs within this process so two overlapping syncs can't process
# the same document at once. The (document_id, chunk_index) unique constraint
# is the database-level backstop.
_sync_lock = threading.Lock()


def sync_knowledge_base(db: Session) -> None:
    """Bring the database in line with the docs folder, then chunk + embed
    whatever needs it."""
    with _sync_lock:
        sync_documents_from_disk(db)
        ensure_all_documents_processed(db)


def process_document(db: Session, document: models.Document) -> list[models.Chunk]:
    """Chunk + embed a document's raw_text, replacing any existing chunks. Idempotent.

    Embeddings are fetched before anything is deleted, so a failed API call
    leaves the existing chunks untouched."""
    pieces = chunk_text(document.raw_text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    embeddings = embed_texts(pieces) if pieces else []

    document.chunks.clear()
    db.flush()

    chunks = [
        models.Chunk(
            document_id=document.id,
            chunk_index=i,
            text=piece,
            embedding=json.dumps(embedding),
            embedding_model=config.EMBEDDING_MODEL,
        )
        for i, (piece, embedding) in enumerate(zip(pieces, embeddings, strict=True))
    ]
    db.add_all(chunks)
    db.commit()
    return chunks


def ensure_all_documents_processed(db: Session) -> None:
    """Chunk + embed every document that has no chunks yet, or has any chunk
    that is missing its embedding or was embedded with a different model than
    the current one. Up-to-date documents are left untouched (no repeat
    embedding calls)."""
    with_chunks = select(models.Chunk.document_id).distinct()
    needs_embedding = (
        select(models.Chunk.document_id)
        .where(
            or_(
                models.Chunk.embedding.is_(None),
                models.Chunk.embedding_model.is_(None),
                models.Chunk.embedding_model != config.EMBEDDING_MODEL,
            )
        )
        .distinct()
    )

    documents = (
        db.query(models.Document)
        .filter(or_(~models.Document.id.in_(with_chunks), models.Document.id.in_(needs_embedding)))
        .all()
    )
    for document in documents:
        process_document(db, document)
