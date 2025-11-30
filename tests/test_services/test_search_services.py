# tests/test_services/test_search_service.py

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from src.services.search_service import SearchService
from src.core.exceptions import IndexNotFound, IndexNotReady
from src.api.schemas import IndexCreate
from src.core.indexing.index_factory import IndexType, Metric

# ============================================================================
# Fakes for Pydantic Models (To avoid ValidationErrors with Mocks)
# ============================================================================


class FakeSearchResult:
    """A logic-less fake for api.schemas.SearchResult."""

    def __init__(self, chunk, similarity):
        self.chunk = chunk
        self.similarity = similarity

    def __repr__(self):
        return f"FakeSearchResult(chunk={self.chunk.uid}, score={self.similarity})"


class FakeIndexMetadata:
    """A logic-less fake for core.models.IndexMetadata."""

    def __init__(self, name, config, vector_count, index_type):
        self.name = name
        self.config = config
        self.vector_count = vector_count
        self.index_type = index_type

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class FakeChunk:
    def __init__(self, uid=None, text="", embedding=None):
        self.uid = uid or uuid4()
        self.text = text
        self.embedding = embedding or [0.1, 0.2]


class FakeDocument:
    def __init__(self, uid=None, chunks=None):
        self.uid = uid or uuid4()
        self.chunks = chunks or {}


class FakeLibrary:
    def __init__(self, uid=None, documents=None, indices=None, index_metadata=None):
        self.uid = uid or uuid4()
        self.documents = documents or {}
        self.indices = indices or {}
        self.index_metadata = index_metadata or {}


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def patch_models(monkeypatch):
    """
    CRITICAL: Replaces real Pydantic models in the service module with Fakes.
    This prevents ValidationError when passing Mocks or FakeChunks.
    """
    monkeypatch.setattr("src.services.search_service.SearchResult", FakeSearchResult)
    monkeypatch.setattr("src.services.search_service.IndexMetadata", FakeIndexMetadata)
    # Note: We don't need to patch IndexConfig if we just pass a Mock/Fake to FakeIndexMetadata


@pytest.fixture
def mock_repo():
    return Mock()


@pytest.fixture
def search_service(mock_repo):
    return SearchService(repository=mock_repo)


@pytest.fixture
def mock_index_factory():
    """Patches the IndexFactory to prevent actual index building."""
    with patch("src.services.search_service.IndexFactory") as mock_factory:
        yield mock_factory


@pytest.fixture
def mock_index_instance():
    """Returns a mock index object that simulates search/build."""
    mock_idx = Mock()
    mock_idx.vector_count = 0
    return mock_idx


# ============================================================================
# Tests
# ============================================================================


def test_create_index_happy_path(
    search_service, mock_repo, mock_index_factory, mock_index_instance
):
    # 1. Setup Data
    lib_id = uuid4()
    chunk1 = FakeChunk(embedding=[1.0, 0.0])
    chunk2 = FakeChunk(embedding=[0.0, 1.0])
    doc = FakeDocument(chunks={chunk1.uid: chunk1, chunk2.uid: chunk2})
    library = FakeLibrary(uid=lib_id, documents={doc.uid: doc})

    mock_repo.get_by_id.return_value = library
    mock_index_factory.create_index.return_value = mock_index_instance

    api_config = IndexCreate(index_type=IndexType.AVL, metric=Metric.COSINE)
    index_name = "test-index"

    # 2. Action
    search_service.create_index(lib_id, index_name, api_config)

    # 3. Assertions
    # Ensure chunks were gathered and passed to build
    mock_index_instance.build.assert_called_once()
    built_chunks = mock_index_instance.build.call_args[0][0]
    assert len(built_chunks) == 2

    # Ensure index was attached to library
    assert index_name in library.indices
    assert library.indices[index_name] == mock_index_instance

    # Ensure metadata was created (It will be our FakeIndexMetadata)
    assert index_name in library.index_metadata
    assert isinstance(library.index_metadata[index_name], FakeIndexMetadata)
    assert library.index_metadata[index_name].vector_count == 2

    # Ensure repository was updated
    mock_repo.update.assert_called_once_with(library)


def test_get_index_status_success(search_service, mock_repo):
    lib_id = uuid4()
    # Use FakeIndexMetadata here instead of the real Pydantic model
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
    """Verifies standard successful search."""
    lib_id = uuid4()
    chunk = FakeChunk(text="result", embedding=[0.1, 0.2])
    doc = FakeDocument(chunks={chunk.uid: chunk})

    # Mock Index behavior
    mock_index = Mock()
    # search returns list of (Chunk, score)
    mock_index.search.return_value = [(chunk, 0.95)]

    library = FakeLibrary(
        uid=lib_id, documents={doc.uid: doc}, indices={"idx": mock_index}
    )
    mock_repo.get_by_id.return_value = library

    results = search_service.search_chunks(lib_id, "idx", [0.1, 0.2], k=1)

    assert len(results) == 1
    # Check that it returns our FakeSearchResult wrapper
    assert isinstance(results[0], FakeSearchResult)
    assert results[0].chunk == chunk
    assert results[0].similarity == 0.95


def test_search_chunks_consistency_check_removes_zombies(search_service, mock_repo):
    """
    CRITICAL TEST: Verifies that if the Index returns a chunk that is NO LONGER
    in the Library (Zombie Data), the service filters it out.
    """
    lib_id = uuid4()

    # 1. Setup: Real chunk exists in Library
    real_chunk = FakeChunk(text="I am real")
    doc = FakeDocument(chunks={real_chunk.uid: real_chunk})

    # 2. Setup: Zombie chunk exists ONLY in the Index (simulating stale state)
    zombie_chunk = FakeChunk(text="I was deleted")

    # 3. Setup: Index returns BOTH
    mock_index = Mock()
    mock_index.search.return_value = [(real_chunk, 0.99), (zombie_chunk, 0.80)]

    library = FakeLibrary(
        uid=lib_id,
        documents={doc.uid: doc},  # Library ONLY has real_chunk
        indices={"idx": mock_index},
    )
    mock_repo.get_by_id.return_value = library

    # 4. Action
    results = search_service.search_chunks(lib_id, "idx", [0.1, 0.1], k=2)

    # 5. Assertion
    # Should contain real_chunk, but NOT zombie_chunk
    assert len(results) == 1
    assert results[0].chunk.uid == real_chunk.uid
    assert results[0].chunk.text == "I am real"


def test_search_chunks_index_not_ready(search_service, mock_repo):
    lib_id = uuid4()
    library = FakeLibrary(uid=lib_id, indices={})  # No indices
    mock_repo.get_by_id.return_value = library

    with pytest.raises(IndexNotReady):
        search_service.search_chunks(lib_id, "missing-idx", [0.1], k=1)
