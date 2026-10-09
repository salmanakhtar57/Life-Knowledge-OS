import enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core import config
from app.database.database import Base


class SourcePlatform(str, enum.Enum):
    PERSONAL = "personal"
    SUBSTACK = "substack"
    MEDIUM = "medium"
    PORTFOLIO = "portfolio"


class Source(Base):
    """A place content comes from: the local docs folder, a Substack publication,
    a Medium feed or a portfolio site. Stored so a source can be re-synced
    without asking for its URL again."""

    __tablename__ = "sources"

    id = Column(BigInteger, primary_key=True)
    platform = Column(
        Enum(
            SourcePlatform,
            name="source_platform",
            values_callable=lambda platforms: [p.value for p in platforms],
        ),
        nullable=False,
    )
    # Feed or site URL; the docs folder uses PERSONAL_SOURCE_URL.
    url = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    documents = relationship(
        "Document", back_populates="source", cascade="all, delete-orphan", passive_deletes=True
    )


class Document(Base):
    """One post, page or local file."""

    __tablename__ = "documents"

    id = Column(BigInteger, primary_key=True)
    source_id = Column(
        BigInteger, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Dedupe key: the post's link, or "file:<name>" for a file in the docs folder.
    url = Column(Text, nullable=False, unique=True)
    title = Column(Text, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    source = relationship("Source", back_populates="documents")
    chunks = relationship(
        "Chunk", back_populates="document", cascade="all, delete-orphan", passive_deletes=True
    )


class Chunk(Base):
    __tablename__ = "chunks"
    # Also serves as the index for lookups by document_id.
    __table_args__ = (UniqueConstraint("document_id", "chunk_index"),)

    id = Column(BigInteger, primary_key=True)
    document_id = Column(
        BigInteger, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(config.EMBEDDING_DIMENSIONS), nullable=False)
    embedding_model = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document = relationship("Document", back_populates="chunks")
