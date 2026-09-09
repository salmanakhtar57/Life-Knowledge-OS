from unittest.mock import MagicMock, patch

from app.services.embeddings import EMBEDDING_MODEL, embed_text


def test_embed_text_returns_vector_from_api():
    fake_embedding = [0.1, 0.2, 0.3]
    fake_response = MagicMock()
    fake_response.data = [MagicMock(embedding=fake_embedding)]

    fake_client = MagicMock()
    fake_client.embeddings.create.return_value = fake_response

    with patch("app.services.embeddings._get_client", return_value=fake_client):
        result = embed_text("hello world")

    assert result == fake_embedding
    fake_client.embeddings.create.assert_called_once_with(
        model=EMBEDDING_MODEL, input="hello world"
    )
