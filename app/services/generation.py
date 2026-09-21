from app.services.openrouter_client import get_client

CHAT_MODEL = "~openai/gpt-sol-latest"


def generate_answer(prompt: str) -> str:
    response = get_client().chat.send(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )
    return response.choices[0].message.content
