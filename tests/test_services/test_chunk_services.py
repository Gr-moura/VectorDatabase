# tests/test_services/test_chunk_services.py
import pytest
from uuid import uuid4, UUID
from unittest.mock import Mock

# Import the service modules under test
from src.services import library_service, document_service, chunk_service

# Import exceptions (these are referenced by the services)
from src.core import exceptions as core_exceptions

from ..fakes import FakeLibrary, FakeDocument, FakeChunk, FakeSchema


# -------------------------
# Fixtures
# -------------------------
@pytest.fixture
def repo_mock():
    return Mock(spec=["add", "get_by_id", "update", "delete", "list_all"])


@pytest.fixture
def embeddings_client_mock():
    """Provides a mock for the embeddings client."""
    mock = Mock(spec=["get_embeddings"])
    mock.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
    return mock


@pytest.fixture(autouse=True)
def patch_models(monkeypatch):
    """
    Replaces real domain models with our fake classes inside the service modules
    to ensure the services are unit tested in isolation.
    """
    monkeypatch.setattr(library_service, "Library", FakeLibrary)
    monkeypatch.setattr(document_service, "Document", FakeDocument)
    monkeypatch.setattr(document_service, "Chunk", FakeChunk)
    monkeypatch.setattr(chunk_service, "Chunk", FakeChunk)


# -------------------------
def test_create_chunk_adds_chunk_and_updates_repo(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )

    lib_id = uuid4()
    doc_id = uuid4()

    # Create a FakeDocument with an empty chunks dict
    fake_doc = FakeDocument(uid=doc_id, chunks={})

    # Create a FakeLibrary containing this document
    fake_lib = FakeLibrary(uid=lib_id, documents={doc_id: fake_doc})
    repo_mock.get_by_id.return_value = fake_lib

    chunk_uid = uuid4()
    chunk_schema = FakeSchema({"uid": chunk_uid, "text": "c"})

    # --- ACTION ---
    created = svc.create_chunk(lib_id, doc_id, chunk_schema)

    # --- ASSERTIONS ---
    assert created.uid == chunk_uid
    assert chunk_uid in fake_doc.chunks
    repo_mock.update.assert_called_once_with(fake_lib)


def test_create_chunk_missing_document_raises(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    lib = FakeLibrary(uid=lib_id, documents={})  # no documents
    repo_mock.get_by_id.return_value = lib

    with pytest.raises(core_exceptions.DocumentNotFound):
        svc.create_chunk(lib_id, uuid4(), FakeSchema({"uid": uuid4()}))


def test_get_chunk_returns_chunk(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    chunk_id = uuid4()
    chunk = FakeChunk(uid=chunk_id, text="x")
    doc = FakeDocument(uid=doc_id, chunks={chunk_id: chunk})
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib

    got = svc.get_chunk(lib_id, doc_id, chunk_id)
    assert got is chunk


def test_get_chunk_missing_document_raises(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib = FakeLibrary(uid=uuid4(), documents={})
    repo_mock.get_by_id.return_value = lib
    with pytest.raises(core_exceptions.DocumentNotFound):
        svc.get_chunk(lib.uid, uuid4(), uuid4())


def test_get_chunk_missing_chunk_raises(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    doc = FakeDocument(uid=doc_id, chunks={})
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib

    with pytest.raises(core_exceptions.ChunkNotFound):
        svc.get_chunk(lib_id, doc_id, uuid4())


def test_list_chunks_returns_list(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    c1 = FakeChunk(uid=uuid4())
    c2 = FakeChunk(uid=uuid4())
    doc = FakeDocument(uid=doc_id, chunks={c1.uid: c1, c2.uid: c2})
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib
    out = svc.list_chunks(lib_id, doc_id)
    assert set(out) == {c1, c2}


def test_update_chunk_merges_and_updates(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    chunk_id = uuid4()
    original = FakeChunk(uid=chunk_id, text="old")
    doc = FakeDocument(uid=doc_id, chunks={chunk_id: original})
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib

    update_schema = FakeSchema({"text": "new"})
    updated = svc.update_chunk(lib_id, doc_id, chunk_id, update_schema)

    repo_mock.update.assert_called_once_with(lib)
    assert isinstance(updated, FakeChunk)
    assert updated.text == "new"
    assert lib.documents[doc_id].chunks[chunk_id] is updated


def test_update_chunk_missing_document_raises(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib = FakeLibrary(uid=uuid4(), documents={})
    repo_mock.get_by_id.return_value = lib
    with pytest.raises(core_exceptions.DocumentNotFound):
        svc.update_chunk(lib.uid, uuid4(), uuid4(), FakeSchema({"text": "x"}))


def test_update_chunk_missing_chunk_raises(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    doc = FakeDocument(uid=doc_id, chunks={})
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib

    with pytest.raises(core_exceptions.ChunkNotFound):
        svc.update_chunk(lib_id, doc_id, uuid4(), FakeSchema({"text": "x"}))


def test_delete_chunk_removes_and_updates(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    chunk_id = uuid4()
    chunk = FakeChunk(uid=chunk_id)
    doc = FakeDocument(uid=doc_id, chunks={chunk_id: chunk})
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib

    svc.delete_chunk(lib_id, doc_id, chunk_id)
    assert chunk_id not in lib.documents[doc_id].chunks
    repo_mock.update.assert_called_once_with(lib)


def test_delete_chunk_missing_document_raises(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib = FakeLibrary(uid=uuid4(), documents={})
    repo_mock.get_by_id.return_value = lib
    with pytest.raises(core_exceptions.DocumentNotFound):
        svc.delete_chunk(lib.uid, uuid4(), uuid4())


def test_delete_chunk_missing_chunk_raises(repo_mock, embeddings_client_mock):
    svc = chunk_service.ChunkService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    doc = FakeDocument(uid=doc_id, chunks={})
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib

    with pytest.raises(core_exceptions.ChunkNotFound):
        svc.delete_chunk(lib_id, doc_id, uuid4())
