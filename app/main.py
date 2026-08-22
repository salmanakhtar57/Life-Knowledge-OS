from fastapi import FastAPI

from app.database import Base, engine
from app.routers import documents

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Life Knowledge OS", version="0.1.0")

app.include_router(documents.router)


@app.get("/health")
def health():
    return {"status": "ok"}
