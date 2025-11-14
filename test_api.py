import pytest
from uuid import uuid4, UUID
from fastapi.testclient import TestClient

from main import app, service
from schemas import (
    LibraryCreate,
    DocumentCreate,
    ChunkCreate,
)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_service():
    """Reset the service state before each test."""
    service.libraries.clear()
    yield
    service.libraries.clear()


@pytest.fixture
def sample_library():
    """Create a sample library for testing."""
    library_data = LibraryCreate(name="Test Library", metadata={"type": "test"})
    return service.create_library(library_data)


@pytest.fixture
def sample_document(sample_library):
    """Create a sample document for testing."""
    doc_data = DocumentCreate(metadata={"source": "test"})
    return service.create_document(sample_library.uid, doc_data)


@pytest.fixture
def sample_chunk(sample_library, sample_document):
    """Create a sample chunk for testing."""
    chunk_data = ChunkCreate(text="Test chunk content", metadata={"page": 1})
    return service.create_chunk(sample_library.uid, sample_document.uid, chunk_data)


# ============================================================================
# ROOT ENDPOINT TESTS
# ============================================================================


def test_index(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Library Service API"}


# ============================================================================
# LIBRARY ENDPOINT TESTS
# ============================================================================


def test_create_library(client):
    """Test creating a new library."""
    response = client.post(
        "/libraries",
        json={"name": "My Library", "metadata": {"description": "Test library"}},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Library"
    assert data["metadata"]["description"] == "Test library"
    assert "id" in data
    assert "documents" in data


def test_create_library_minimal(client):
    """Test creating a library with minimal data."""
    response = client.post("/libraries", json={"name": "Minimal Library"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Minimal Library"
    assert data["metadata"] == {}


def test_create_library_invalid_name(client):
    """Test creating a library with invalid name."""
    response = client.post("/libraries", json={"name": ""})
    assert response.status_code == 422


def test_get_library(client, sample_library):
    """Test retrieving a specific library."""
    response = client.get(f"/libraries/{sample_library.uid}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_library.uid)
    assert data["name"] == sample_library.name


def test_get_library_not_found(client):
    """Test retrieving a non-existent library."""
    fake_id = uuid4()
    response = client.get(f"/libraries/{fake_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_libraries_empty(client):
    """Test listing libraries when none exist."""
    response = client.get("/libraries")
    assert response.status_code == 200
    assert response.json() == []


def test_list_libraries(client):
    """Test listing multiple libraries."""
    client.post("/libraries", json={"name": "Library 1"})
    client.post("/libraries", json={"name": "Library 2"})
    client.post("/libraries", json={"name": "Library 3"})

    response = client.get("/libraries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    names = [lib["name"] for lib in data]
    assert "Library 1" in names
    assert "Library 2" in names
    assert "Library 3" in names


def test_update_library(client, sample_library):
    """Test updating a library."""
    response = client.put(
        f"/libraries/{sample_library.uid}",
        json={"name": "Updated Library", "metadata": {"updated": True}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Library"
    assert data["metadata"]["updated"] is True


def test_update_library_partial(client, sample_library):
    """Test partial update of a library."""
    response = client.put(
        f"/libraries/{sample_library.uid}", json={"name": "Partially Updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Partially Updated"
    assert data["metadata"] == sample_library.metadata


def test_update_library_not_found(client):
    """Test updating a non-existent library."""
    fake_id = uuid4()
    response = client.put(f"/libraries/{fake_id}", json={"name": "Should Fail"})
    assert response.status_code == 404


def test_delete_library(client, sample_library):
    """Test deleting a library."""
    response = client.delete(f"/libraries/{sample_library.uid}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/libraries/{sample_library.uid}")
    assert get_response.status_code == 404


def test_delete_library_not_found(client):
    """Test deleting a non-existent library."""
    fake_id = uuid4()
    response = client.delete(f"/libraries/{fake_id}")
    assert response.status_code == 404


# ============================================================================
# DOCUMENT ENDPOINT TESTS
# ============================================================================


def test_create_document(client, sample_library):
    """Test creating a document in a library."""
    response = client.post(
        f"/libraries/{sample_library.uid}/documents",
        json={"metadata": {"title": "Test Document"}},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["metadata"]["title"] == "Test Document"
    assert data["library_uid"] == str(sample_library.uid)
    assert "id" in data
    assert "chunks" in data


def test_create_document_minimal(client, sample_library):
    """Test creating a document with minimal data."""
    response = client.post(f"/libraries/{sample_library.uid}/documents", json={})
    assert response.status_code == 201
    data = response.json()
    assert data["metadata"] == {}


def test_create_document_library_not_found(client):
    """Test creating a document in a non-existent library."""
    fake_id = uuid4()
    response = client.post(f"/libraries/{fake_id}/documents", json={"metadata": {}})
    assert response.status_code == 404


def test_get_document(client, sample_library, sample_document):
    """Test retrieving a specific document."""
    response = client.get(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_document.uid)
    assert data["library_uid"] == str(sample_library.uid)


def test_get_document_not_found(client, sample_library):
    """Test retrieving a non-existent document."""
    fake_id = uuid4()
    response = client.get(f"/libraries/{sample_library.uid}/documents/{fake_id}")
    assert response.status_code == 404


def test_get_document_library_not_found(client):
    """Test retrieving a document from a non-existent library."""
    fake_lib_id = uuid4()
    fake_doc_id = uuid4()
    response = client.get(f"/libraries/{fake_lib_id}/documents/{fake_doc_id}")
    assert response.status_code == 404


def test_list_documents_empty(client, sample_library):
    """Test listing documents when none exist."""
    response = client.get(f"/libraries/{sample_library.uid}/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_list_documents(client, sample_library):
    """Test listing multiple documents."""
    client.post(
        f"/libraries/{sample_library.uid}/documents", json={"metadata": {"doc": 1}}
    )
    client.post(
        f"/libraries/{sample_library.uid}/documents", json={"metadata": {"doc": 2}}
    )

    response = client.get(f"/libraries/{sample_library.uid}/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for doc in data:
        assert doc["library_uid"] == str(sample_library.uid)


def test_update_document(client, sample_library, sample_document):
    """Test updating a document."""
    response = client.put(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}",
        json={"metadata": {"updated": True}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["updated"] is True


def test_update_document_not_found(client, sample_library):
    """Test updating a non-existent document."""
    fake_id = uuid4()
    response = client.put(
        f"/libraries/{sample_library.uid}/documents/{fake_id}", json={"metadata": {}}
    )
    assert response.status_code == 404


def test_delete_document(client, sample_library, sample_document):
    """Test deleting a document."""
    response = client.delete(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}"
    )
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}"
    )
    assert get_response.status_code == 404


def test_delete_document_not_found(client, sample_library):
    """Test deleting a non-existent document."""
    fake_id = uuid4()
    response = client.delete(f"/libraries/{sample_library.uid}/documents/{fake_id}")
    assert response.status_code == 404


# ============================================================================
# CHUNK ENDPOINT TESTS
# ============================================================================


def test_create_chunk(client, sample_library, sample_document):
    """Test creating a chunk in a document."""
    response = client.post(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks",
        json={
            "text": "This is chunk text",
            "metadata": {"page": 1},
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "This is chunk text"
    assert data["metadata"]["page"] == 1
    assert data["library_uid"] == str(sample_library.uid)
    assert data["document_uid"] == str(sample_document.uid)
    assert "id" in data


def test_create_chunk_minimal(client, sample_library, sample_document):
    """Test creating a chunk with minimal data."""
    response = client.post(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks",
        json={"text": "Minimal chunk"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Minimal chunk"
    assert data["embedding"] is None
    assert data["metadata"] == {}


def test_create_chunk_invalid_text(client, sample_library, sample_document):
    """Test creating a chunk with invalid text."""
    response = client.post(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks",
        json={"text": ""},
    )
    assert response.status_code == 422


def test_create_chunk_document_not_found(client, sample_library):
    """Test creating a chunk in a non-existent document."""
    fake_id = uuid4()
    response = client.post(
        f"/libraries/{sample_library.uid}/documents/{fake_id}/chunks",
        json={"text": "Test"},
    )
    assert response.status_code == 404


def test_get_chunk(client, sample_library, sample_document, sample_chunk):
    """Test retrieving a specific chunk."""
    response = client.get(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks/{sample_chunk.uid}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_chunk.uid)
    assert data["text"] == sample_chunk.text
    assert data["library_uid"] == str(sample_library.uid)
    assert data["document_uid"] == str(sample_document.uid)


def test_get_chunk_not_found(client, sample_library, sample_document):
    """Test retrieving a non-existent chunk."""
    fake_id = uuid4()
    response = client.get(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks/{fake_id}"
    )
    assert response.status_code == 404


def test_list_chunks_empty(client, sample_library, sample_document):
    """Test listing chunks when none exist."""
    response = client.get(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks"
    )
    assert response.status_code == 200
    assert response.json() == []


def test_list_chunks(client, sample_library, sample_document):
    """Test listing multiple chunks."""
    client.post(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks",
        json={"text": "Chunk 1"},
    )
    client.post(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks",
        json={"text": "Chunk 2"},
    )

    response = client.get(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for chunk in data:
        assert chunk["library_uid"] == str(sample_library.uid)
        assert chunk["document_uid"] == str(sample_document.uid)


def test_update_chunk(client, sample_library, sample_document, sample_chunk):
    """Test updating a chunk."""
    response = client.put(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks/{sample_chunk.uid}",
        json={
            "text": "Updated chunk text",
            "metadata": {"updated": True},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Updated chunk text"
    assert data["metadata"]["updated"] is True


def test_update_chunk_partial(client, sample_library, sample_document, sample_chunk):
    """Test partial update of a chunk."""
    response = client.put(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks/{sample_chunk.uid}",
        json={"text": "Only text updated"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Only text updated"
    assert data["metadata"] == sample_chunk.metadata


def test_update_chunk_not_found(client, sample_library, sample_document):
    """Test updating a non-existent chunk."""
    fake_id = uuid4()
    response = client.put(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks/{fake_id}",
        json={"text": "Should fail"},
    )
    assert response.status_code == 404


def test_delete_chunk(client, sample_library, sample_document, sample_chunk):
    """Test deleting a chunk."""
    response = client.delete(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks/{sample_chunk.uid}"
    )
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks/{sample_chunk.uid}"
    )
    assert get_response.status_code == 404


def test_delete_chunk_not_found(client, sample_library, sample_document):
    """Test deleting a non-existent chunk."""
    fake_id = uuid4()
    response = client.delete(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks/{fake_id}"
    )
    assert response.status_code == 404


# ============================================================================
# CASCADE AND RELATIONSHIP TESTS
# ============================================================================


def test_library_contains_documents(client, sample_library):
    """Test that a library properly contains its documents."""
    # Create multiple documents
    doc1 = client.post(
        f"/libraries/{sample_library.uid}/documents",
        json={"metadata": {"name": "doc1"}},
    ).json()
    doc2 = client.post(
        f"/libraries/{sample_library.uid}/documents",
        json={"metadata": {"name": "doc2"}},
    ).json()

    # Get library and verify it has documents
    library_response = client.get(f"/libraries/{sample_library.uid}")
    library_data = library_response.json()

    assert len(library_data["documents"]) == 2
    doc_ids = list(library_data["documents"].keys())
    assert doc1["id"] in doc_ids
    assert doc2["id"] in doc_ids


def test_document_contains_chunks(client, sample_library, sample_document):
    """Test that a document properly contains its chunks."""
    # Create multiple chunks
    chunk1 = client.post(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks",
        json={"text": "Chunk 1"},
    ).json()
    chunk2 = client.post(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}/chunks",
        json={"text": "Chunk 2"},
    ).json()

    # Get document and verify it has chunks
    doc_response = client.get(
        f"/libraries/{sample_library.uid}/documents/{sample_document.uid}"
    )
    doc_data = doc_response.json()

    assert len(doc_data["chunks"]) == 2
    chunk_ids = list(doc_data["chunks"].keys())
    assert chunk1["id"] in chunk_ids
    assert chunk2["id"] in chunk_ids


def test_invalid_uuid_format(client):
    """Test endpoints with invalid UUID format."""
    response = client.get("/libraries/not-a-uuid")
    assert response.status_code == 422
