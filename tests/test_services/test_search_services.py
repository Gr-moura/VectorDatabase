# tests/test_services/test_search_service.py

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from src.services.search_service import SearchService
from src.core.exceptions import IndexNotFound, IndexNotReady, VectorDimensionMismatch
from src.api.schemas import IndexCreate
from src.core.indexing.index_factory import IndexType, Metric
from fastapi import status

from ..fakes import (
    FakeLibrary,
    FakeDocument,
    FakeChunk,
    FakeChunkResponse,
    FakeSearchResult,
    FakeIndexMetadata,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def patch_models(monkeypatch):
    monkeypatch.setattr("src.services.search_service.SearchResult", FakeSearchResult)
    monkeypatch.setattr("src.services.search_service.IndexMetadata", FakeIndexMetadata)
    monkeypatch.setattr("src.services.search_service.ChunkResponse", FakeChunkResponse)


@pytest.fixture
def mock_repo():
    return Mock()


@pytest.fixture
def mock_embeddings_client():
    """Mock for the embeddings provider."""
    client = Mock()
    # Default behavior: return a dummy vector
    client.get_embeddings.return_value = [[0.1, 0.2]]
    return client


@pytest.fixture
def search_service(mock_repo, mock_embeddings_client):
    return SearchService(repository=mock_repo, embeddings_client=mock_embeddings_client)


@pytest.fixture
def mock_index_factory():
    with patch("src.services.search_service.IndexFactory") as mock_factory:
        yield mock_factory


@pytest.fixture
def mock_index_instance():
    mock_idx = Mock()
    mock_idx.vector_count = 0
    return mock_idx


# ============================================================================
# Tests
# ============================================================================


def test_create_index_happy_path(
    search_service, mock_repo, mock_index_factory, mock_index_instance
):
    lib_id = uuid4()
    chunk1 = FakeChunk(embedding=[1.0, 0.0])
    chunk2 = FakeChunk(embedding=[0.0, 1.0])
    doc = FakeDocument(chunks={chunk1.uid: chunk1, chunk2.uid: chunk2})
    library = FakeLibrary(uid=lib_id, documents={doc.uid: doc})

    mock_repo.get_by_id.return_value = library
    mock_index_factory.create_index.return_value = mock_index_instance

    api_config = IndexCreate(index_type=IndexType.AVL, metric=Metric.COSINE)
    index_name = "test-index"

    search_service.create_index(lib_id, index_name, api_config)

    mock_index_instance.build.assert_called_once()
    assert index_name in library.indices
    assert library.indices[index_name] == mock_index_instance
    assert index_name in library.index_metadata
    mock_repo.update.assert_called_once_with(library)


def test_get_index_status_success(search_service, mock_repo):
    lib_id = uuid4()
    meta = FakeIndexMetadata(
        name="idx", config=Mock(), vector_count=10, index_type="avl"
    )
    library = FakeLibrary(uid=lib_id, index_metadata={"idx": meta})
    mock_repo.get_by_id.return_value = library

    result = search_service.get_index_status(lib_id, "idx")
    assert result == meta


def test_get_index_status_not_found(search_service, mock_repo):
    lib_id = uuid4()
    library = FakeLibrary(uid=lib_id, index_metadata={})
    mock_repo.get_by_id.return_value = library

    with pytest.raises(IndexNotFound):
        search_service.get_index_status(lib_id, "missing-index")


def test_delete_index_success(search_service, mock_repo):
    lib_id = uuid4()
    index_obj = Mock()
    meta = Mock()
    library = FakeLibrary(
        uid=lib_id, indices={"idx": index_obj}, index_metadata={"idx": meta}
    )
    mock_repo.get_by_id.return_value = library

    search_service.delete_index(lib_id, "idx")

    assert "idx" not in library.indices
    assert "idx" not in library.index_metadata
    mock_repo.update.assert_called_once_with(library)


def test_delete_index_not_found(search_service, mock_repo):
    lib_id = uuid4()
    library = FakeLibrary(uid=lib_id)
    mock_repo.get_by_id.return_value = library

    with pytest.raises(IndexNotFound):
        search_service.delete_index(lib_id, "non-existent")


def test_search_chunks_success(search_service, mock_repo):
    lib_id = uuid4()
    chunk = FakeChunk(text="result", embedding=[0.1, 0.2])
    doc = FakeDocument(chunks={chunk.uid: chunk})

    mock_index = Mock()
    mock_index.search.return_value = [(chunk, 0.95)]

    library = FakeLibrary(
        uid=lib_id, documents={doc.uid: doc}, indices={"idx": mock_index}
    )
    mock_repo.get_by_id.return_value = library

    # Pass manual embedding
    results = search_service.search_chunks(
        lib_id, "idx", k=1, query_embedding=[0.1, 0.2]
    )

    assert len(results) == 1
    assert isinstance(results[0], FakeSearchResult)
    assert isinstance(results[0].chunk, FakeChunkResponse)
    assert results[0].chunk.id == chunk.uid
    assert results[0].chunk.document_id == doc.uid
    assert results[0].similarity == 0.95


def test_search_chunks_with_text_query(
    search_service, mock_repo, mock_embeddings_client
):
    """
    Tests if the service generates the embedding when it receives text and calls the index correctly.
    """
    lib_id = uuid4()
    chunk = FakeChunk()
    doc = FakeDocument(chunks={chunk.uid: chunk})

    mock_index = Mock()
    mock_index.search.return_value = [(chunk, 0.99)]

    library = FakeLibrary(
        uid=lib_id, documents={doc.uid: doc}, indices={"idx": mock_index}
    )
    mock_repo.get_by_id.return_value = library

    # Setup mock embedding return
    generated_vector = [0.9, 0.9]
    mock_embeddings_client.get_embeddings.return_value = [generated_vector]

    # Action: Pass text instead of vector
    search_service.search_chunks(lib_id, "idx", k=1, query_text="search for me")

    # Assertions
    # 1. Verifies if the embeddings client was called correctly (input_type='search_query')
    mock_embeddings_client.get_embeddings.assert_called_once_with(
        texts=["search for me"], input_type="search_query"
    )

    # 2. Verifies if the generated vector was passed to the index
    mock_index.search.assert_called_once_with(generated_vector, 1)


def test_search_chunks_consistency_check_removes_zombies(search_service, mock_repo):
    lib_id = uuid4()

    real_chunk = FakeChunk(text="I am real")
    doc = FakeDocument(chunks={real_chunk.uid: real_chunk})

    zombie_chunk = FakeChunk(text="I was deleted")

    mock_index = Mock()
    mock_index.search.return_value = [(real_chunk, 0.99), (zombie_chunk, 0.80)]

    library = FakeLibrary(
        uid=lib_id, documents={doc.uid: doc}, indices={"idx": mock_index}
    )
    mock_repo.get_by_id.return_value = library

    results = search_service.search_chunks(
        lib_id, "idx", k=2, query_embedding=[0.1, 0.1]
    )

    assert len(results) == 1
    assert results[0].chunk.id == real_chunk.uid
    assert results[0].chunk.text == "I am real"


def test_search_chunks_index_not_ready(search_service, mock_repo):
    lib_id = uuid4()
    library = FakeLibrary(uid=lib_id, indices={})
    mock_repo.get_by_id.return_value = library

    with pytest.raises(IndexNotReady):
        search_service.search_chunks(lib_id, "missing-idx", k=1, query_embedding=[0.1])


def test_search_chunks_fails_gracefully_with_wrong_vector_dimension(
    search_service, mock_repo
):
    """
    Unit Test: Verifies that the service captures NumPy errors raised by the index
    and wraps them in a semantic VectorDimensionMismatch exception.
    """
    lib_id = uuid4()

    # 1. Setup: Mock the index to raise ValueError (simulating NumPy mismatch)
    mock_index = Mock()
    mock_index.search.side_effect = ValueError("shapes (3,) and (2,) not aligned")

    library = FakeLibrary(
        uid=lib_id, indices={"idx": mock_index}, index_metadata={"idx": Mock()}
    )
    mock_repo.get_by_id.return_value = library

    # 2. Action & Assert
    # Expect the specific custom exception, not a generic ValueError
    with pytest.raises(VectorDimensionMismatch) as exc_info:
        search_service.search_chunks(lib_id, "idx", k=1, query_embedding=[0.1, 0.2])

    # 3. Verify the exception message
    error_msg = str(exc_info.value)
    assert "Vector dimension mismatch" in error_msg
    assert "shapes (3,) and (2,) not aligned" in error_msg
