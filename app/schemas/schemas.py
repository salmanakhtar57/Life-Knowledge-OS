from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class DocumentCreate(BaseModel):
    title: str
    text: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty")
        return v


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    source_type: str
    uploaded_at: datetime


class DocumentDetail(DocumentListItem):
    raw_text: str


class ChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chunk_index: int
    text: str


class ProcessResult(BaseModel):
    document_id: int
    chunk_count: int
    chunks: list[ChunkOut]


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