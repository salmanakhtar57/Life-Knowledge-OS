import pytest

from app.services.chunking import chunk_text


def test_text_shorter_than_chunk_size_returns_single_chunk():
    assert chunk_text("hello world", chunk_size=1000, overlap=200) == ["hello world"]


def test_exact_boundaries_and_count():
    text = "a" * 25
    chunks = chunk_text(text, chunk_size=10, overlap=4)
    # step = 6 -> starts at 0, 6, 12, 18, 24
    assert chunks == ["a" * 10, "a" * 10, "a" * 10, "a" * 7, "a" * 1]


def test_overlap_is_real():
    text = "0123456789" * 3  # 30 chars
    chunks = chunk_text(text, chunk_size=10, overlap=4)
    for i in range(len(chunks) - 1):
        assert chunks[i][-4:] == chunks[i + 1][:4]


def test_zero_overlap_no_repeated_content():
    text = "0123456789" * 3  # 30 chars
    chunks = chunk_text(text, chunk_size=10, overlap=0)
    assert chunks == ["0123456789", "0123456789", "0123456789"]


def test_empty_string_returns_empty_list():
    assert chunk_text("", chunk_size=100, overlap=10) == []


def test_whitespace_only_returns_empty_list():
    assert chunk_text("   \n\t  ", chunk_size=100, overlap=10) == []


@pytest.mark.parametrize(
    "chunk_size,overlap",
    [
        (0, 0),
        (-10, 0),
        (100, -1),
        (100, 100),
        (100, 150),
    ],
)
def test_invalid_params_raise_value_error(chunk_size, overlap):
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=chunk_size, overlap=overlap)
