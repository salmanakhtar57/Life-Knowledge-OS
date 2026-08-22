# Life Knowledge OS

Personal RAG system. Phase 1 MVP: document ingestion only (chunking, embeddings, and
retrieval/generation come in later steps — see `mvp.md` and `CLAUDE.md`).

## Stack

FastAPI + SQLAlchemy + SQLite.

## Running locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

uvicorn app.main:app --reload
```

The app boots at `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`.

Data is stored in `life_knowledge_os.db` (SQLite file, created automatically on first run,
persists between restarts).

## Endpoints (Step 1 — Document Ingestion)

- `POST /documents` — create a document. Either:
  - `multipart/form-data` with a `file` field — accepted types:
    `.txt`, `.md`, `.json`, `.csv`, `.html`/`.htm`, `.rtf`, `.log` (decoded as UTF-8), and `.pdf`
    (text extracted via `pypdf`; scanned/image-only PDFs with no extractable text are rejected).
    DOCX and other binary formats are still not supported, or
  - `application/json` body: `{"title": "...", "text": "..."}`
- `GET /documents` — list all documents (id, title, source_type, uploaded_at)
- `GET /documents/{id}` — full document detail, including `raw_text`

## Roadmap (not built yet, on purpose)

- Chunking
- Embeddings
- Vector search
- `/ask` endpoint (retrieval + generation)
- Minimal frontend
