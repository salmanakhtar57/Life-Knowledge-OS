from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, Field


# =========================
# Documents
# =========================

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


# =========================
# Ask / RAG
# =========================

class AskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be empty")
        return value


class SourceOut(BaseModel):
    document_id: int
    document_title: str
    chunk_id: int
    chunk_index: int
    snippet: str

    # Additional source information for Noteway
    source_platform: str = "personal"
    document_url: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceOut]


# =========================
# Auth
# =========================

class Token(BaseModel):
    access_token: str
    token_type: str


# =========================
# Substack
# =========================

class SubstackSyncRequest(BaseModel):
    url: str


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    published_at: datetime | None
    created_at: datetime


class PostSyncResponse(BaseModel):
    fetched: int
    new: int
    skipped_duplicates: int
    skipped_empty: int
    message: str
    already_running: bool = False


# =========================
# Noteway statistics
# =========================

class StatsResponse(BaseModel):
    substack_posts: int
    faq_documents: int
    last_published_at: datetime | None
    days_since_last_post: int | None
    last_synced_at: datetime | None


class WritingIdea(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)


class WritingIdeasResponse(BaseModel):
    summary: str = Field(min_length=1)
    ideas: list[str] = Field(max_length=3)
