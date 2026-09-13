from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

# Search upward from this file's own location for the project's .env, so the
# key loads correctly regardless of the directory the app was started from.
load_dotenv(find_dotenv())

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client
