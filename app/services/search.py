from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core import config
from app.models.models import Chunk, Document, Source, SourcePlatform


def top_k_chunks(
    db: Session,
    query_embedding: list[float],
    k: int = 5,
    min_similarity: float = 0.0,
    platform: SourcePlatform | None = None,
) -> list[Chunk]:
    """Cosine-similarity ranking done by Postgres (pgvector). Returns at most `k`
    chunks embedded with the current model, and only those scoring at least
    `min_similarity`, most similar first. `platform` limits the search to one
    source platform."""
    distance = Chunk.embedding.cosine_distance(query_embedding)
    query = (
        select(Chunk)
        .join(Chunk.document)
        .options(joinedload(Chunk.document).joinedload(Document.source))
        .where(
            Chunk.embedding_model == config.EMBEDDING_MODEL,
            # cosine similarity = 1 - cosine distance
            distance <= 1 - min_similarity,
        )
        .order_by(distance)
        .limit(k)
    )
    if platform is not None:
        query = query.join(Document.source).where(Source.platform == platform)
    return list(db.scalars(query))
