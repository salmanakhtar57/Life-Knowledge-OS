from dotenv import find_dotenv, load_dotenv
from openrouter import OpenRouter
import os

load_dotenv(find_dotenv())

_client: OpenRouter | None = None


def get_client() -> OpenRouter:
    global _client

    if _client is None:
        _client = OpenRouter(
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

    return _client