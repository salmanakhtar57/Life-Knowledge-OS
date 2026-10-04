from openrouter import OpenRouter

from app.core import config

_client: OpenRouter | None = None


class AIServiceError(Exception):
    """An embedding or chat call to the AI provider failed. The message is for
    server logs only; clients get a generic response (see app.main)."""


def get_client() -> OpenRouter:
    global _client

    if _client is None:
        _client = OpenRouter(api_key=config.OPENROUTER_API_KEY)

    return _client
