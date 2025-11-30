# tests/test_services/test_library_services.py
import pytest
from uuid import uuid4
from unittest.mock import Mock

# Import the service modules under test
from src.services import library_service, document_service, chunk_service


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
