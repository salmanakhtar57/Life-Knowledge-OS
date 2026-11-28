
# Life Knowledge OS (Noteway)

A personal knowledge and writing dashboard that brings my Substack and Medium content into one place.

Noteway uses AI and Retrieval-Augmented Generation (RAG) to help me explore my writing, find relevant information, and get answers based on my own published content.

## Features

- **Substack Integration:** Sync and browse published Substack posts.
- **Medium Integration:** Sync and browse Medium articles.
- **Ask AI:** Ask questions about your writing and retrieve relevant information using RAG.
- **Writing Suggestions:** Generate new writing ideas based on existing articles.
- **Dashboard Stats:** View publication counts and recent publishing activity.
- **Theme Support:** Light, dark, and system themes.

## Tech Stack

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Frontend | React, TypeScript, Vite |
| Database | PostgreSQL, pgvector |
| AI | OpenRouter, LLMs, Embeddings |
| RAG | Chunking, Embeddings, Vector Search |
| Integrations | Substack, Medium |

## How RAG Works

The application uses a RAG pipeline to retrieve relevant content before generating an answer.

```text
Substack / Medium Content
          |
          v
     Data Sync
          |
          v
       Chunking
          |
          v
      Embeddings
          |
          v
  PostgreSQL + pgvector
          |
          v
    User Question
          |
          v
   Vector Retrieval
          |
          v
   LLM + Retrieved Context
          |
          v
     AI Response
```

This approach helps ground AI responses in my own writing rather than relying only on the model's general knowledge.

## Running Locally

### Backend

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env and update the values

# Start the backend
python -m app.main
```

Backend API: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

npm install

# Configure frontend environment variables
# Copy .env.example to .env

npm run dev
```

Open the local URL provided by Vite, usually `http://localhost:5173`.

## Project Structure

```text
Life-Knowledge-OS/
├── app/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   └── services/
├── frontend/
│   └── src/
├── .env.example
├── requirements.txt
└── README.md
```

## Future Improvements

- Integrate Substack Notes.
- Organize and integrate interview experiences.
- Expand Ask AI to cover additional personal knowledge sources.
- Improve retrieval quality and evaluation.
- Explore more insights from writing history.

---

**Status:** Actively developed.
