import httpx
from openrouter.errors import NoResponseError, OpenRouterError, ResponseValidationError

from app.core import config
from app.services.openrouter_client import AIServiceError, get_client


def generate_answer(prompt: str) -> str:
    try:
        response = get_client().chat.send(
            model=config.CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config.CHAT_MAX_TOKENS,
            timeout_ms=int(config.AI_REQUEST_TIMEOUT_SECONDS * 1000),
        )
    except (OpenRouterError, NoResponseError, ResponseValidationError, httpx.HTTPError) as exc:
        raise AIServiceError(f"Chat request failed: {exc}") from exc

    content = response.choices[0].message.content if response.choices else None
    if not isinstance(content, str) or not content.strip():
        raise AIServiceError("Chat request returned no text content")
    return content.strip()
