from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def embed_text(text: str) -> list[float]:
    """Embed a string via OpenAI. No I/O beyond the API call itself."""
    response = _get_client().embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding
