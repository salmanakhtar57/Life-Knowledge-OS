from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.embeddings import embed_text
from app.services.generation import generate_answer
from app.services.prompting import build_prompt
from app.services.search import top_k_chunks

router = APIRouter(prefix="/ask", tags=["ask"])

TOP_K = 5
SNIPPET_LENGTH = 200


@router.post("", response_model=schemas.AskResponse)
def ask_question(payload: schemas.AskRequest, db: Session = Depends(get_db)):
    question = payload.question.strip()

    chunks = db.query(models.Chunk).filter(models.Chunk.embedding.isnot(None)).all()
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No processed documents to search yet. Upload and process a document first.",
        )

    query_embedding = embed_text(question)
    top_chunks = top_k_chunks(chunks, query_embedding, k=TOP_K)

    document_ids = {chunk.document_id for chunk in top_chunks}
    documents = db.query(models.Document).filter(models.Document.id.in_(document_ids)).all()
    title_by_id = {document.id: document.title for document in documents}

    prompt = build_prompt(
        question,
        [(title_by_id[chunk.document_id], chunk.text) for chunk in top_chunks],
    )
    answer = generate_answer(prompt)

    return schemas.AskResponse(
        answer=answer,
        sources=[
            schemas.SourceOut(
                document_id=chunk.document_id,
                document_title=title_by_id[chunk.document_id],
                chunk_id=chunk.id,
                chunk_index=chunk.chunk_index,
                snippet=chunk.text[:SNIPPET_LENGTH],
            )
            for chunk in top_chunks
        ],
    )
