from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source_type: str
    uploaded_at: datetime


class DocumentDetail(DocumentListItem):
    raw_text: str


class SyncResult(BaseModel):
    document_count: int
    chunk_count: int


class AskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("question must not be empty")
        return v


class SourceOut(BaseModel):
    document_id: int
    document_title: str
    chunk_id: int
    chunk_index: int
    snippet: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceOut]