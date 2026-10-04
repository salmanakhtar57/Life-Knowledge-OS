from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import config
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.embeddings import embed_text
from app.services.generation import generate_answer
from app.services.prompting import NO_ANSWER, build_prompt
from app.services.search import top_k_chunks

router = APIRouter(prefix="/ask", tags=["ask"])

SNIPPET_LENGTH = 200


@router.post("", response_model=schemas.AskResponse)
def ask_question(payload: schemas.AskRequest, db: Session = Depends(get_db)):
    question = payload.question.strip()

    chunks = (
        db.query(models.Chunk)
        .filter(
            models.Chunk.embedding.is_not(None),
            models.Chunk.embedding_model == config.EMBEDDING_MODEL,
        )
        .all()
    )
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents have been added yet.",
        )

    query_embedding = embed_text(question)
    top_chunks = top_k_chunks(
        chunks, query_embedding, k=config.TOP_K, min_similarity=config.MIN_SIMILARITY
    )
    if not top_chunks:
        return schemas.AskResponse(answer=NO_ANSWER, sources=[])

    prompt = build_prompt(question, [(chunk.document.title, chunk.text) for chunk in top_chunks])
    answer = generate_answer(prompt)

    return schemas.AskResponse(
        answer=answer,
        sources=[
            schemas.SourceOut(
                document_id=chunk.document_id,
                document_title=chunk.document.title,
                chunk_id=chunk.id,
                chunk_index=chunk.chunk_index,
                snippet=chunk.text[:SNIPPET_LENGTH],
            )
            for chunk in top_chunks
        ],
    )
