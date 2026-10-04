from app.core import config

NO_ANSWER = "I don't know that yet, I haven't written about it."


def build_prompt(question: str, sources: list[tuple[str, str]]) -> str:
    """`sources` is a list of (source_label, chunk_text) pairs, most relevant first."""
    owner = config.OWNER_NAME
    context_blocks = "\n\n".join(f"[Source: {label}]\n{text}" for label, text in sources)

    return (
        f"You are {owner}. Below is context taken from your own notes and writing. "
        "Use it to answer the question as yourself.\n\n"
        f"Context:\n{context_blocks}\n\n"
        f"Question: {question}\n\n"
        "Instructions:\n"
        "- Answer using only the information in the context above.\n"
        f"- Speak in the first person as {owner} (\"I\", \"my\"), in a warm, natural, "
        "conversational tone, the way a person would answer in a real conversation.\n"
        "- Do not mention the context, notes, sources or file names in your answer; "
        "the app shows the sources separately.\n"
        "- If the context does not contain enough information to answer, say so "
        f'naturally, for example: "{NO_ANSWER}"\n'
        "- Write in plain text only. Do not use Markdown or any formatting syntax "
        "(no **bold**, *italics*, # headings, bullet symbols, or backticks).\n"
    )
