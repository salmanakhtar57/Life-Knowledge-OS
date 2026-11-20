from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    published_at: datetime | None
    created_at: datetime


class DocumentDetail(DocumentListItem):
    raw_text: str


class SyncResult(BaseModel):
    document_count: int
    chunk_count: int


class UploadResult(BaseModel):
    id: int
    title: str
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


class Token(BaseModel):
    access_token: str
    token_type: str


# Paste into app/schemas/schemas.py (your existing imports already cover BaseModel).


class SubstackSyncRequest(BaseModel):
    url: str  # "name.substack.com", "https://name.substack.com", or a custom domain


class SyncResult(BaseModel):
    fetched: int
    new: int
    skipped_duplicates: int
    skipped_empty: int


# --- Replace your existing SourceOut with this version (adds two optional fields) ---
class SourceOut(BaseModel):
    document_id: int
    document_title: str
    chunk_id: int
    chunk_index: int
    snippet: str
    source_platform: str = "personal"   # "personal" | "substack" | "medium" | "portfolio"
    document_url: str | None = None     # link to the post; None for local files