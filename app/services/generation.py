from app.services.openai_client import get_client

CHAT_MODEL = "gpt-4o-mini"


def generate_answer(prompt: str) -> str:
    response = get_client().chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
