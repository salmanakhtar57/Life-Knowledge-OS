import json
import math

from app.models.models import Chunk


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def top_k_chunks(chunks: list[Chunk], query_embedding: list[float], k: int = 5) -> list[Chunk]:
    """Brute-force cosine similarity ranking. `chunks` must already be loaded
    (e.g. from a DB query) — this function does no I/O itself."""
    scored = [
        (chunk, _cosine_similarity(json.loads(chunk.embedding), query_embedding))
        for chunk in chunks
        if chunk.embedding is not None
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [chunk for chunk, _ in scored[:k]]
