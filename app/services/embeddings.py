import requests

from app.core import config
from app.services.openrouter_client import AIServiceError

EMBEDDINGS_URL = f"{config.OPENROUTER_BASE_URL}/embeddings"


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed many strings via OpenRouter, sending them in batches instead of
    one request per string. Returns embeddings in the same order as `texts`."""
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), config.EMBEDDING_BATCH_SIZE):
        embeddings.extend(_embed_batch(texts[start : start + config.EMBEDDING_BATCH_SIZE]))
    return embeddings


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]


def _embed_batch(batch: list[str]) -> list[list[float]]:
    try:
        response = requests.post(
            EMBEDDINGS_URL,
            headers={
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": config.EMBEDDING_MODEL, "input": batch},
            timeout=config.AI_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()["data"]
        items = sorted(data, key=lambda item: item.get("index", 0))
        embeddings = [item["embedding"] for item in items]
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        raise AIServiceError(f"Embedding request failed: {exc}") from exc

    if len(embeddings) != len(batch):
        raise AIServiceError(
            f"Embedding request returned {len(embeddings)} embeddings for {len(batch)} inputs"
        )
    return embeddings
