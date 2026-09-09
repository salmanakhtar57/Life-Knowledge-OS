def build_prompt(question: str, sources: list[tuple[str, str]]) -> str:
    """`sources` is a list of (source_label, chunk_text) pairs, most relevant first."""
    context_blocks = "\n\n".join(f"[Source: {label}]\n{text}" for label, text in sources)

    return (
        "You are answering a question using only the context below, taken from the "
        "user's own notes.\n\n"
        f"Context:\n{context_blocks}\n\n"
        f"Question: {question}\n\n"
        "Instructions:\n"
        "- Answer using only the information in the context above.\n"
        "- If the context does not contain enough information to answer, say "
        '"I don\'t know based on your notes."\n'
        "- Cite which source(s) you used in your answer.\n"
    )
