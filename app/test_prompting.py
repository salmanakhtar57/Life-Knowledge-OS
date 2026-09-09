from app.services.prompting import build_prompt


def test_prompt_includes_question():
    prompt = build_prompt("What is Life Knowledge OS?", [("my-notes.md", "It's a RAG system.")])
    assert "What is Life Knowledge OS?" in prompt


def test_prompt_includes_all_source_labels_and_text():
    sources = [("note-a.md", "content A"), ("note-b.md", "content B")]
    prompt = build_prompt("question", sources)
    for label, text in sources:
        assert label in prompt
        assert text in prompt


def test_prompt_instructs_dont_know_fallback():
    prompt = build_prompt("question", [("note.md", "text")])
    assert "don't know" in prompt.lower()


def test_prompt_instructs_citing_sources():
    prompt = build_prompt("question", [("note.md", "text")])
    assert "cite" in prompt.lower()
