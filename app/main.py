from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.database.database import Base, SessionLocal, engine
from app.core.routing import api_router
from app.services.document_sync import sync_documents_from_disk

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    sync_documents_from_disk(db)
finally:
    db.close()

app = FastAPI(title="Life Knowledge OS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)