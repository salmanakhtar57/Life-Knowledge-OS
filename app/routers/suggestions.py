
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.schemas import WritingIdeasResponse
from app.services.writing_ideas import (
    get_substack_writing_ideas,
    refresh_substack_writing_ideas,
    get_medium_writing_ideas,
    refresh_medium_writing_ideas,
)

router = APIRouter(tags=["writing-ideas"])


@router.get("/substack/writing-ideas", response_model=WritingIdeasResponse)
def get_substack_suggestions(db: Session = Depends(get_db)):
    return get_substack_writing_ideas(db)


@router.post("/substack/writing-ideas/refresh", response_model=WritingIdeasResponse)
def refresh_substack_suggestions(db: Session = Depends(get_db)):
    return refresh_substack_writing_ideas(db)


@router.get("/medium/writing-ideas", response_model=WritingIdeasResponse)
def get_medium_suggestions(db: Session = Depends(get_db)):
    return get_medium_writing_ideas(db)


@router.post("/medium/writing-ideas/refresh", response_model=WritingIdeasResponse)
def refresh_medium_suggestions(db: Session = Depends(get_db)):
    return refresh_medium_writing_ideas(db)
