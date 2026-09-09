from unittest.mock import MagicMock, patch

from app.services.generation import CHAT_MODEL, generate_answer


def test_generate_answer_returns_model_reply():
    fake_message = MagicMock(content="This is the answer.")
    fake_choice = MagicMock(message=fake_message)
    fake_response = MagicMock(choices=[fake_choice])

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_response

    with patch("app.services.generation.get_client", return_value=fake_client):
        result = generate_answer("some prompt")

    assert result == "This is the answer."
    fake_client.chat.completions.create.assert_called_once_with(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": "some prompt"}],
    )
