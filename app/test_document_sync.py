from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models import models
from app.services import document_sync


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_sync_creates_document_from_new_file(tmp_path, monkeypatch):
    (tmp_path / "faqs.txt").write_text("Some FAQ content", encoding="utf-8")
    monkeypatch.setattr(document_sync, "DOCS_DIR", tmp_path)

    db = _session()
    document_sync.sync_documents_from_disk(db)

    documents = db.query(models.Document).all()
    assert len(documents) == 1
    assert documents[0].title == "faqs.txt"
    assert documents[0].raw_text == "Some FAQ content"


def test_sync_updates_changed_file_and_clears_its_chunks(tmp_path, monkeypatch):
    file_path = tmp_path / "faqs.txt"
    file_path.write_text("Old content", encoding="utf-8")
    monkeypatch.setattr(document_sync, "DOCS_DIR", tmp_path)

    db = _session()
    document_sync.sync_documents_from_disk(db)
    document = db.query(models.Document).one()
    db.add(models.Chunk(document_id=document.id, chunk_index=0, text="old chunk", embedding="[]"))
    db.commit()

    file_path.write_text("New content", encoding="utf-8")
    document_sync.sync_documents_from_disk(db)

    db.refresh(document)
    assert document.raw_text == "New content"
    remaining_chunks = db.query(models.Chunk).filter(models.Chunk.document_id == document.id)
    assert remaining_chunks.count() == 0


def test_sync_does_not_duplicate_unchanged_file(tmp_path, monkeypatch):
    (tmp_path / "faqs.txt").write_text("Same content", encoding="utf-8")
    monkeypatch.setattr(document_sync, "DOCS_DIR", tmp_path)

    db = _session()
    document_sync.sync_documents_from_disk(db)
    document_sync.sync_documents_from_disk(db)

    assert db.query(models.Document).count() == 1


def test_sync_reads_any_filename_not_just_faqs(tmp_path, monkeypatch):
    (tmp_path / "random-notes.md").write_text("Some notes", encoding="utf-8")
    monkeypatch.setattr(document_sync, "DOCS_DIR", tmp_path)

    db = _session()
    document_sync.sync_documents_from_disk(db)

    document = db.query(models.Document).one()
    assert document.title == "random-notes.md"
    assert document.source_type == "md"


def test_sync_skips_missing_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(document_sync, "DOCS_DIR", tmp_path / "does-not-exist")

    db = _session()
    document_sync.sync_documents_from_disk(db)

    assert db.query(models.Document).count() == 0
