from openrouter import OpenRouter

from app.core import config

_client: OpenRouter | None = None


def get_client() -> OpenRouter:
    global _client

    if _client is None:
        _client = OpenRouter(api_key=config.OPENROUTER_API_KEY)

    return _client
