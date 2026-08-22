from fastapi import FastAPI
import uvicorn
from app.database.database import Base, engine
from app.core.routing import api_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Life Knowledge OS", version="0.1.0")

app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)