# Life Knowledge OS

A personal AI assistant that answers questions from your own notes instead of
the model's general knowledge. Ask a question in plain English and get a short,
first-person answer drawn only from your notes, with the notes it came from
shown as tags.

It's a retrieval-augmented generation (RAG) pipeline built from scratch:
chunking, embeddings, vector search and grounded generation, with no RAG
framework.

**Status:** Phase 1 (MVP) is complete. Phase 2 (Substack, Medium and portfolio
content) is next; see the roadmap below.

## How it works

```
FAQs/*.txt ──► sync to SQLite ──► split into chunks ──► embed each chunk
                                                            │
question ──► embed ──► cosine similarity vs. all chunks ──► top matches
                                                            │
               prompt: "answer only from this context" ──► LLM ──► answer + sources
```

1. **Notes:** every text file in `FAQs/` is a document. Files get there
   either by being put in the folder or by being uploaded through the UI or
   `POST /documents/upload`. The folder is the source of truth: new, edited
   and deleted files are reflected in the database on the next sync.
2. **Chunking:** documents are split into chunks of up to 1,000 characters
   that overlap slightly. Splits happen between paragraphs, then sentences,
   then words, never in the middle of a word.
3. **Embedding:** each chunk is converted to a vector with
   `openai/text-embedding-3-small` (through OpenRouter) and stored next to its
   text.
4. **Retrieval:** the question is embedded the same way. The 5 most similar
   chunks above a minimum similarity score are selected.
5. **Generation:** the chunks and the question go to the chat model, which is
   told to answer only from that context. If no chunk is relevant enough, the
   app answers "I don't know" without calling the model.
6. **Response:** the answer plus the source chunks (document title, position
   and a snippet).

Syncing (steps 1–3) runs when the server starts, after each upload, and on
`POST /documents/sync`. Only new or changed documents are embedded.

## Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite
- **AI:** OpenRouter (embeddings and chat)
- **Auth:** OAuth2 password flow with JWT (PyJWT, pwdlib/argon2)
- **Frontend:** React 18, TypeScript, Vite

## Project structure

```
app/
├── main.py              # app setup, startup sync, CORS, error handling
├── core/
│   ├── config.py        # all settings, read from .env
│   ├── routing.py       # registers the routers
│   └── security.py      # owner login, JWT, protected-route dependency
├── database/            # engine and session
├── models/              # Document, Chunk
├── schemas/             # request/response models
├── routers/
│   ├── ask.py           # POST /ask
│   ├── documents.py     # /documents (owner only)
│   └── user_routes.py   # /auth
└── services/
    ├── document_sync.py # FAQs/ folder → database
    ├── chunking.py      # text → chunks
    ├── embeddings.py    # chunks → vectors (batched)
    ├── processing.py    # sync + chunk + embed
    ├── search.py        # cosine similarity, top-k
    ├── prompting.py     # the grounded prompt
    ├── generation.py    # chat call
    └── openrouter_client.py
frontend/                # React app
FAQs/                    # your notes (the knowledge base)
```

## Running locally

### 1. Backend

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env         # then fill in the values (see below)

python -m app.main
```

The API runs at `http://localhost:8000`, with interactive docs at
`http://localhost:8000/docs`. On startup, the server creates
`life_knowledge_os.db` if it doesn't exist and syncs `FAQs/` into it.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env         # VITE_API_URL=http://localhost:8000
npm run dev
```

Open the URL Vite prints, usually `http://localhost:5173`. The backend accepts
requests from `localhost` and `127.0.0.1` on any port.

### 3. Add notes

Either:

- **In the UI:** choose a `.txt` or `.md` file (up to 1 MB) under the question
  box and click **Upload**. It's saved
  into `FAQs/`, chunked and embedded straight away.
- **On disk:** put text files in `FAQs/`, then restart the server or call
  `POST /documents/sync` with the owner's token.

## Configuration

All settings live in `.env`; see `.env.example`. Only `OPENROUTER_API_KEY` is
required to ask questions. Everything else has a default.

| Variable | Default | Purpose |
|---|---|---|
| `OPENROUTER_API_KEY` | — | Required for embeddings and answers |
| `CHAT_MODEL` | `~openai/gpt-sol-latest` | Model that writes the answers |
| `EMBEDDING_MODEL` | `openai/text-embedding-3-small` | Changing it re-embeds everything on the next sync |
| `TOP_K` | `5` | Maximum chunks sent to the model |
| `MIN_SIMILARITY` | `0.15` | Chunks scoring below this are ignored |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `1000` / `200` | Chunk size and overlap, in characters |
| `OWNER_NAME` | `Salman` | Name the assistant answers as |
| `AUTH_USERNAME`, `AUTH_PASSWORD_HASH`, `JWT_SECRET_KEY` | — | Owner login (see below) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | How long a login token lasts |
| `UPLOAD_MAX_BYTES` | `1048576` | Maximum upload size (1 MB) |

## Authentication

There is a single owner account, configured in `.env`. There is no sign-up
and no users table. `/ask`, `/health` and `/documents/upload` are public.
Listing, reading and syncing documents need the owner's token, because they
expose the raw notes and trigger embedding calls for the whole folder.

Generate the values with the venv active:

```bash
python -c "from pwdlib import PasswordHash; print(PasswordHash.recommended().hash('YOUR-PASSWORD'))"
python -c "import secrets; print(secrets.token_hex(32))"
```

Put them in `.env`, keeping the single quotes around the hash because it
contains `$` signs:

```
AUTH_USERNAME=your-username
AUTH_PASSWORD_HASH='<first output>'
JWT_SECRET_KEY=<second output>
```

In `/docs`, click **Authorize**, enter the username and the plain password,
and the protected endpoints will work.

## API

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/ask` | Public | `{"question": "..."}` → `{"answer": "...", "sources": [...]}` |
| `GET` | `/health` | Public | Health check |
| `POST` | `/auth/token` | Public | Log in (form fields `username`, `password`) → bearer token |
| `GET` | `/documents` | Owner | List documents |
| `GET` | `/documents/{id}` | Owner | One document, including its full text |
| `POST` | `/documents/upload` | Public | Upload a `.txt`/`.md` file (multipart field `file`, max 1 MB) → saved into `FAQs/`, then synced |
| `POST` | `/documents/sync` | Owner | Re-read `FAQs/`, then chunk and embed anything new or changed |

If the AI provider fails (outage, rate limit, invalid key), the API returns
`503` with a generic message. Details are written to the server log only.

## Roadmap

- **Phase 2:** add Substack, Medium and portfolio content, tagged by
  platform; a stats strip; a "recently added" panel; platform filters; topic
  suggestions; and automatic sync on a schedule.
- **Later:** hybrid search and reranking, a proper vector database, an
  evaluation setup, caching, and conversation memory.
