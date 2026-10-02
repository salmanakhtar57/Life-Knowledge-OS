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


def test_sync_removes_document_whose_file_was_deleted(tmp_path, monkeypatch):
    file_path = tmp_path / "old-notes.txt"
    file_path.write_text("Old notes", encoding="utf-8")
    (tmp_path / "faqs.txt").write_text("Some FAQ content", encoding="utf-8")
    monkeypatch.setattr(document_sync, "DOCS_DIR", tmp_path)

    db = _session()
    document_sync.sync_documents_from_disk(db)
    old = db.query(models.Document).filter(models.Document.title == "old-notes.txt").one()
    db.add(models.Chunk(document_id=old.id, chunk_index=0, text="old chunk", embedding="[]"))
    db.commit()

    file_path.unlink()
    document_sync.sync_documents_from_disk(db)

    assert [d.title for d in db.query(models.Document).all()] == ["faqs.txt"]
    assert db.query(models.Chunk).count() == 0


def test_sync_removes_documents_not_backed_by_a_file(tmp_path, monkeypatch):
    (tmp_path / "faqs.txt").write_text("Some FAQ content", encoding="utf-8")
    monkeypatch.setattr(document_sync, "DOCS_DIR", tmp_path)

    db = _session()
    db.add(models.Document(title="Cover Letter.pdf", source_type="pdf", raw_text="Dear ..."))
    db.commit()

    document_sync.sync_documents_from_disk(db)

    assert [d.title for d in db.query(models.Document).all()] == ["faqs.txt"]


def test_sync_collapses_duplicate_documents_for_same_file(tmp_path, monkeypatch):
    (tmp_path / "faqs.txt").write_text("Some FAQ content", encoding="utf-8")
    monkeypatch.setattr(document_sync, "DOCS_DIR", tmp_path)

    db = _session()
    for _ in range(2):
        db.add(models.Document(title="faqs.txt", source_type="txt", raw_text="Some FAQ content"))
    db.commit()
    duplicate_id = db.query(models.Document).order_by(models.Document.id.desc()).first().id
    db.add(models.Chunk(document_id=duplicate_id, chunk_index=0, text="dup chunk", embedding="[]"))
    db.commit()

    document_sync.sync_documents_from_disk(db)

    assert db.query(models.Document).count() == 1
    assert db.query(models.Chunk).filter(models.Chunk.document_id == duplicate_id).count() == 0
