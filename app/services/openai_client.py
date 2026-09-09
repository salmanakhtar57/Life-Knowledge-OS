from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client
