from app.services.openai_client import get_client

EMBEDDING_MODEL = "text-embedding-3-small"


def embed_text(text: str) -> list[float]:
    """Embed a string via OpenAI. No I/O beyond the API call itself."""
    response = get_client().embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding
