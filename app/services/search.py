import json
import math

from app.models.models import Chunk


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"Embedding dimensions differ ({len(a)} vs {len(b)})")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def top_k_chunks(
    chunks: list[Chunk],
    query_embedding: list[float],
    k: int = 5,
    min_similarity: float = 0.0,
) -> list[Chunk]:
    """Brute-force cosine similarity ranking. Returns at most `k` chunks, and
    only those scoring at least `min_similarity`, most similar first. `chunks`
    must already be loaded and embedded with the same model as the query
    (e.g. from a DB query) — this function does no I/O itself."""
    scored = []
    for chunk in chunks:
        if chunk.embedding is None:
            continue
        score = _cosine_similarity(json.loads(chunk.embedding), query_embedding)
        if score >= min_similarity:
            scored.append((chunk, score))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [chunk for chunk, _ in scored[:k]]
