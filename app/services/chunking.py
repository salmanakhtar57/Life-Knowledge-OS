import re

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_OVERLAP = 200

_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks of at most `chunk_size` characters,
    breaking only between paragraphs, then sentences, then words — never
    mid-word (unless a single word is longer than `chunk_size`). Each chunk
    starts with the last whole pieces of the previous one, up to `overlap`
    characters.

    No I/O, no DB — pure string in, list of strings out.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must not be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    units = _split_into_units(text, chunk_size)
    if not units:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for unit in units:
        if current and current_len + 1 + len(unit) > chunk_size:
            chunks.append("\n".join(current))
            current, current_len = _overlap_tail(current, overlap)
            while current and current_len + 1 + len(unit) > chunk_size:
                removed = current.pop(0)
                current_len -= len(removed) + (1 if current else 0)

        current_len += len(unit) + (1 if current else 0)
        current.append(unit)

    chunks.append("\n".join(current))
    return chunks


def _split_into_units(text: str, chunk_size: int) -> list[str]:
    """Break text into the largest natural pieces that each fit in a chunk."""
    units: list[str] = []
    for paragraph in _PARAGRAPH_BREAK.split(text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= chunk_size:
            units.append(paragraph)
            continue
        for sentence in _SENTENCE_END.split(paragraph):
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(sentence) <= chunk_size:
                units.append(sentence)
            else:
                units.extend(_split_by_words(sentence, chunk_size))
    return units


def _split_by_words(text: str, chunk_size: int) -> list[str]:
    pieces: list[str] = []
    current = ""
    for word in text.split():
        if len(word) > chunk_size:
            if current:
                pieces.append(current)
                current = ""
            pieces.extend(word[i : i + chunk_size] for i in range(0, len(word), chunk_size))
            continue
        candidate = f"{current} {word}" if current else word
        if len(candidate) > chunk_size:
            pieces.append(current)
            current = word
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def _overlap_tail(units: list[str], overlap: int) -> tuple[list[str], int]:
    """The trailing units of a finished chunk that fit within `overlap` characters."""
    tail: list[str] = []
    tail_len = 0
    for unit in reversed(units):
        added = len(unit) + (1 if tail else 0)
        if tail_len + added > overlap:
            break
        tail.insert(0, unit)
        tail_len += added
    return tail, tail_len
