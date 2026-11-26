from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.schemas import WritingIdeasResponse
from app.services.writing_ideas import get_writing_ideas

router = APIRouter(prefix="/writing-ideas", tags=["writing-ideas"])


@router.get("", response_model=WritingIdeasResponse)
def generate_writing_ideas(db: Session = Depends(get_db)):
    return get_writing_ideas(db)