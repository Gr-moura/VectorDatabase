# tests/test_services/test_services.py
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
# Tests for LibraryService
# -------------------------
def test_create_library_calls_repo_add(repo_mock):
    svc = library_service.LibraryService(repository=repo_mock)
    data = {"uid": uuid4(), "name": "my lib"}
    schema = FakeSchema(data)

    lib = svc.create_library(schema)

    repo_mock.add.assert_called_once()
    added = repo_mock.add.call_args[0][0]
    assert isinstance(added, FakeLibrary)
    assert added.name == "my lib"
    assert isinstance(lib, FakeLibrary)
    assert lib.name == "my lib"


def test_get_library_calls_repo_get_by_id(repo_mock):
    svc = library_service.LibraryService(repository=repo_mock)
    lib_id = uuid4()
    fake_lib = FakeLibrary(uid=lib_id)
    repo_mock.get_by_id.return_value = fake_lib

    got = svc.get_library(lib_id)
    repo_mock.get_by_id.assert_called_once_with(lib_id)
    assert got is fake_lib


def test_update_library_merges_and_updates(repo_mock):
    svc = library_service.LibraryService(repository=repo_mock)
    lib_id = uuid4()
    current = FakeLibrary(uid=lib_id, name="old")
    repo_mock.get_by_id.return_value = current

    update_schema = FakeSchema({"name": "new"})
    updated = svc.update_library(lib_id, update_schema)

    repo_mock.update.assert_called_once()
    called_obj = repo_mock.update.call_args[0][0]
    assert isinstance(called_obj, FakeLibrary)
    assert called_obj.name == "new"
    assert updated.name == "new"


def test_delete_library_delegates_to_repo(repo_mock):
    svc = library_service.LibraryService(repository=repo_mock)
    lib_id = uuid4()
    svc.delete_library(lib_id)
    repo_mock.delete.assert_called_once_with(lib_id)


def test_list_libraries_returns_repo_list_all(repo_mock):
    svc = library_service.LibraryService(repository=repo_mock)
    repo_mock.list_all.return_value = ["a", "b"]
    assert svc.list_libraries() == ["a", "b"]
    repo_mock.list_all.assert_called_once()


# -------------------------
# Tests for DocumentService
# -------------------------
def test_create_document_adds_document_and_chunks(repo_mock, embeddings_client_mock):
    svc = document_service.DocumentService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    lib = FakeLibrary(uid=lib_id, documents={})
    repo_mock.get_by_id.return_value = lib

    doc_uid = uuid4()
    chunk_uid = uuid4()
    # chunk schema is FakeSchema, as the service expects chunk_create.model_dump()
    doc_schema = FakeSchema(
        {
            "uid": doc_uid,
            "title": "doc1",
            "chunks": [FakeSchema({"uid": chunk_uid, "text": "hello"})],
        }
    )

    created = svc.create_document(lib_id, doc_schema)

    # library should have the new document (either in lib.documents or created returned)
    assert created.uid == doc_uid
    repo_mock.update.assert_called_once_with(lib)
    assert isinstance(created, FakeDocument)


def test_get_document_not_found_raises(repo_mock, embeddings_client_mock):
    svc = document_service.DocumentService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    lib = FakeLibrary(uid=lib_id, documents={})
    repo_mock.get_by_id.return_value = lib

    with pytest.raises(core_exceptions.DocumentNotFound):
        svc.get_document(lib_id, uuid4())


def test_get_document_returns_document(repo_mock, embeddings_client_mock):
    svc = document_service.DocumentService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    doc = FakeDocument(uid=doc_id)
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib

    got = svc.get_document(lib_id, doc_id)
    assert got is doc


def test_list_documents_returns_all(repo_mock, embeddings_client_mock):
    svc = document_service.DocumentService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc1 = FakeDocument(uid=uuid4())
    doc2 = FakeDocument(uid=uuid4())
    lib = FakeLibrary(uid=lib_id, documents={doc1.uid: doc1, doc2.uid: doc2})
    repo_mock.get_by_id.return_value = lib

    out = svc.list_documents(lib_id)
    assert set(out) == {doc1, doc2}


def test_update_document_merges_and_updates(repo_mock, embeddings_client_mock):
    svc = document_service.DocumentService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    doc = FakeDocument(uid=doc_id, title="old")
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib

    update_schema = FakeSchema({"title": "new"})
    updated = svc.update_document(lib_id, doc_id, update_schema)

    repo_mock.update.assert_called_once_with(lib)
    assert isinstance(updated, FakeDocument)
    assert updated.title == "new"
    assert lib.documents[doc_id] is updated


def test_delete_document_deletes_and_updates_repo(repo_mock, embeddings_client_mock):
    svc = document_service.DocumentService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    doc_id = uuid4()
    doc = FakeDocument(uid=doc_id)
    lib = FakeLibrary(uid=lib_id, documents={doc_id: doc})
    repo_mock.get_by_id.return_value = lib

    svc.delete_document(lib_id, doc_id)
    assert doc_id not in lib.documents
    repo_mock.update.assert_called_once_with(lib)


def test_delete_document_missing_raises(repo_mock, embeddings_client_mock):
    svc = document_service.DocumentService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    lib = FakeLibrary(uid=lib_id, documents={})
    repo_mock.get_by_id.return_value = lib

    with pytest.raises(core_exceptions.DocumentNotFound):
        svc.delete_document(lib_id, uuid4())


def test_create_document_generates_embeddings_for_nested_chunks(
    repo_mock, embeddings_client_mock
):
    """
    Verify that creating a document with chunks triggers batch embedding generation.
    """
    svc = document_service.DocumentService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()
    fake_lib = FakeLibrary(uid=lib_id, documents={}, indices={}, index_metadata={})
    repo_mock.get_by_id.return_value = fake_lib

    # Configure the mock to return embeddings for our batch
    # We are sending 2 chunks, so we expect 2 vectors back
    embeddings_client_mock.get_embeddings.return_value = [[0.1, 0.1], [0.2, 0.2]]

    doc_uid = uuid4()
    doc_schema = FakeSchema(
        {
            "uid": doc_uid,
            "title": "My Doc",
            "chunks": [
                FakeSchema({"text": "chunk A"}),
                FakeSchema({"text": "chunk B"}),
            ],
        }
    )

    created_doc = svc.create_document(lib_id, doc_schema)

    # 1. Verify client call
    # It should call get_embeddings ONCE with a list of BOTH texts
    embeddings_client_mock.get_embeddings.assert_called_once_with(
        ["chunk A", "chunk B"]
    )

    # 2. Verify embeddings were assigned
    # Note: created_doc.chunks is a dict {uid: Chunk}
    chunks_list = list(created_doc.chunks.values())
    assert len(chunks_list) == 2

    # Sort by text to ensure we check the right ones (since dict order can vary)
    chunks_list.sort(key=lambda c: c.text)

    assert chunks_list[0].text == "chunk A"
    assert chunks_list[0].embedding == [0.1, 0.1]

    assert chunks_list[1].text == "chunk B"
    assert chunks_list[1].embedding == [0.2, 0.2]


def test_create_document_updates_indices_for_nested_chunks(
    repo_mock, embeddings_client_mock
):
    """
    Verify that creating a document also updates the library's indices.
    """
    svc = document_service.DocumentService(
        repository=repo_mock, embeddings_client=embeddings_client_mock
    )
    lib_id = uuid4()

    # Setup a library with an AVL index
    # We use a real AvlIndex here to verify the insertion logic
    from src.core.indexing.avl_index import AvlIndex

    avl_index = AvlIndex()
    fake_lib = FakeLibrary(
        uid=lib_id,
        documents={},
        indices={"my-avl": avl_index},
        index_metadata={"my-avl": Mock(vector_count=0)},  # Mock metadata
    )
    repo_mock.get_by_id.return_value = fake_lib
    embeddings_client_mock.get_embeddings.return_value = [[0.1], [0.2]]

    doc_schema = FakeSchema(
        {"chunks": [FakeSchema({"text": "A"}), FakeSchema({"text": "B"})]}
    )

    svc.create_document(lib_id, doc_schema)

    # Verify the index actually received the vectors
    assert avl_index.vector_count == 2


# -------------------------
# Tests for ChunkService
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
