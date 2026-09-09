import json

from app.models.models import Chunk
from app.services.search import top_k_chunks


def _chunk(id, text, embedding):
    return Chunk(id=id, document_id=1, chunk_index=id, text=text, embedding=json.dumps(embedding))


def test_most_similar_chunk_ranks_first():
    relevant = _chunk(1, "relevant", [1.0, 0.0])
    unrelated = _chunk(2, "unrelated", [0.0, 1.0])
    somewhat = _chunk(3, "somewhat", [0.7, 0.7])

    results = top_k_chunks([unrelated, somewhat, relevant], query_embedding=[1.0, 0.0], k=3)

    assert [c.id for c in results] == [1, 3, 2]


def test_k_limits_result_count():
    chunks = [_chunk(i, f"chunk {i}", [1.0, 0.0]) for i in range(10)]
    results = top_k_chunks(chunks, query_embedding=[1.0, 0.0], k=3)
    assert len(results) == 3


def test_chunks_without_embedding_are_skipped():
    embedded = _chunk(1, "embedded", [1.0, 0.0])
    unprocessed = Chunk(id=2, document_id=1, chunk_index=1, text="unprocessed", embedding=None)

    results = top_k_chunks([unprocessed, embedded], query_embedding=[1.0, 0.0], k=5)

    assert [c.id for c in results] == [1]


def test_empty_chunk_list_returns_empty():
    assert top_k_chunks([], query_embedding=[1.0, 0.0], k=5) == []
