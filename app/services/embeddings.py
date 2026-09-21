import os
import requests

from app.services.openrouter_client import get_client

EMBEDDING_MODEL = "openai/text-embedding-3-small"


def embed_text(text: str) -> list[float]:

    """Embed a string via OpenRouter. No I/O beyond the API call itself."""

    response = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
        },
    )

    response.raise_for_status()

    data = response.json()

    return data["data"][0]["embedding"]