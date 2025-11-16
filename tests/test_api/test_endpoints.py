# vector_db_project/tests/test_api/test_endpoints.py

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from main import app
from src.api.dependencies import (
    library_repository,
)  # Import the singleton for state management


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_repository():
    """Reset the repository state before each test run."""
    library_repository.clear()
    yield
    library_repository.clear()


# ============================================================================
# HELPER FUNCTIONS FOR TEST SETUP
# ============================================================================


def create_library_via_api(client: TestClient, metadata: dict = None) -> dict:
    """Helper to create a library and return its JSON data."""
    if metadata is None:
        metadata = {"name": "Default Test Library"}
    response = client.post("/libraries/", json={"metadata": metadata})
    assert response.status_code == 201, f"Failed to create library: {response.text}"
    return response.json()


def create_document_via_api(
    client: TestClient, library_id: str, metadata: dict = None
) -> dict:
    """Helper to create a document and return its JSON data."""
    if metadata is None:
        metadata = {"title": "Default Test Doc"}
    response = client.post(
        f"/libraries/{library_id}/documents", json={"metadata": metadata}
    )
    assert response.status_code == 201, f"Failed to create document: {response.text}"
    return response.json()


def create_chunk_via_api(
    client: TestClient, library_id: str, document_id: str, payload: dict
) -> dict:
    """Helper to create a chunk and return its JSON data."""
    response = client.post(
        f"/libraries/{library_id}/documents/{document_id}/chunks", json=payload
    )
    assert response.status_code == 201, f"Failed to create chunk: {response.text}"
    return response.json()


# ============================================================================
# ROOT ENDPOINT TESTS (1 test)
# ============================================================================
def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Vector DB API"}


# ============================================================================
# LIBRARY ENDPOINT TESTS (10 tests)
# ============================================================================
def test_create_library(client):
    response = client.post(
        "/libraries/",
        json={"metadata": {"name": "My Library", "description": "Test library"}},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["metadata"]["name"] == "My Library"
    assert data["metadata"]["description"] == "Test library"


def test_create_library_minimal(client):
    response = client.post(
        "/libraries/", json={"metadata": {"name": "Minimal Library"}}
    )
    assert response.status_code == 201
    assert response.json()["metadata"]["name"] == "Minimal Library"


def test_get_library(client):
    lib_data = create_library_via_api(client, {"name": "Test Library", "type": "test"})
    lib_id = lib_data["id"]
    response = client.get(f"/libraries/{lib_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lib_id
    assert data["metadata"]["name"] == "Test Library"


def test_get_library_not_found(client):
    response = client.get(f"/libraries/{uuid4()}")
    assert response.status_code == 404


def test_list_libraries_empty(client):
    response = client.get("/libraries/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_libraries(client):
    create_library_via_api(client, {"name": "Library 1"})
    create_library_via_api(client, {"name": "Library 2"})
    response = client.get("/libraries/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {"Library 1", "Library 2"} == {lib["metadata"]["name"] for lib in data}


def test_update_library(client):
    lib_data = create_library_via_api(client, {"name": "Original"})
    lib_id = lib_data["id"]
    response = client.put(
        f"/libraries/{lib_id}", json={"metadata": {"name": "Updated", "new": True}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["name"] == "Updated"
    assert data["metadata"]["new"] is True


def test_update_library_partial(client):
    lib_data = create_library_via_api(client, {"name": "Original", "persistent": True})
    lib_id = lib_data["id"]
    response = client.put(
        f"/libraries/{lib_id}", json={"metadata": {"name": "Partially Updated"}}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["name"] == "Partially Updated"
    assert "persistent" not in data["metadata"]  # Pydantic model replaces the dict


def test_update_library_not_found(client):
    response = client.put(f"/libraries/{uuid4()}", json={"metadata": {}})
    assert response.status_code == 404


def test_delete_library(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    response = client.delete(f"/libraries/{lib_id}")
    assert response.status_code == 204
    assert client.get(f"/libraries/{lib_id}").status_code == 404


# ============================================================================
# DOCUMENT ENDPOINT TESTS (10 tests)
# ============================================================================
def test_create_document(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    response = client.post(
        f"/libraries/{lib_id}/documents", json={"metadata": {"title": "Test Doc"}}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["metadata"]["title"] == "Test Doc"
    assert data["library_id"] == lib_id


def test_create_document_minimal(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    response = client.post(f"/libraries/{lib_id}/documents", json={})
    assert response.status_code == 201
    assert response.json()["metadata"] == {}


def test_create_document_library_not_found(client):
    response = client.post(f"/libraries/{uuid4()}/documents", json={})
    assert response.status_code == 404


def test_get_document(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    doc_data = create_document_via_api(client, lib_id)
    doc_id = doc_data["id"]
    response = client.get(f"/libraries/{lib_id}/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["id"] == doc_id


def test_get_document_not_found(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    response = client.get(f"/libraries/{lib_id}/documents/{uuid4()}")
    assert response.status_code == 404


def test_list_documents_empty(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    response = client.get(f"/libraries/{lib_id}/documents")
    assert response.status_code == 200
    assert response.json() == []


def test_list_documents(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    create_document_via_api(client, lib_id)
    create_document_via_api(client, lib_id)
    response = client.get(f"/libraries/{lib_id}/documents")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_document(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    doc_data = create_document_via_api(client, lib_id, {"title": "Old Title"})
    doc_id = doc_data["id"]
    response = client.put(
        f"/libraries/{lib_id}/documents/{doc_id}", json={"metadata": {"updated": True}}
    )
    assert response.status_code == 200
    assert response.json()["metadata"] == {"updated": True}


def test_update_document_not_found(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    response = client.put(f"/libraries/{lib_id}/documents/{uuid4()}", json={})
    assert response.status_code == 404


def test_delete_document(client):
    lib_data = create_library_via_api(client)
    lib_id = lib_data["id"]
    doc_data = create_document_via_api(client, lib_id)
    doc_id = doc_data["id"]
    response = client.delete(f"/libraries/{lib_id}/documents/{doc_id}")
    assert response.status_code == 204
    assert client.get(f"/libraries/{lib_id}/documents/{doc_id}").status_code == 404


# ============================================================================
# CHUNK ENDPOINT TESTS (12 tests)
# ============================================================================
def test_create_chunk(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    payload = {"text": "This is chunk text", "metadata": {"page": 1}}
    response = client.post(
        f"/libraries/{lib['id']}/documents/{doc['id']}/chunks", json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "This is chunk text"
    assert data["metadata"]["page"] == 1
    assert data["library_id"] == lib["id"]
    assert data["document_id"] == doc["id"]


def test_create_chunk_minimal(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    response = client.post(
        f"/libraries/{lib['id']}/documents/{doc['id']}/chunks", json={"text": "Minimal"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Minimal"
    assert data["embedding"] is None
    assert data["metadata"] == {}


def test_create_chunk_invalid_text(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    response = client.post(
        f"/libraries/{lib['id']}/documents/{doc['id']}/chunks", json={"text": ""}
    )
    assert response.status_code == 422


def test_create_chunk_document_not_found(client):
    lib = create_library_via_api(client)
    response = client.post(
        f"/libraries/{lib['id']}/documents/{uuid4()}/chunks", json={"text": "Fail"}
    )
    assert response.status_code == 404


def test_get_chunk(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    chunk = create_chunk_via_api(client, lib["id"], doc["id"], {"text": "Content"})
    response = client.get(
        f"/libraries/{lib['id']}/documents/{doc['id']}/chunks/{chunk['id']}"
    )
    assert response.status_code == 200
    assert response.json()["id"] == chunk["id"]


def test_get_chunk_not_found(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    response = client.get(
        f"/libraries/{lib['id']}/documents/{doc['id']}/chunks/{uuid4()}"
    )
    assert response.status_code == 404


def test_list_chunks_empty(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    response = client.get(f"/libraries/{lib['id']}/documents/{doc['id']}/chunks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_chunks(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    create_chunk_via_api(client, lib["id"], doc["id"], {"text": "c1"})
    create_chunk_via_api(client, lib["id"], doc["id"], {"text": "c2"})
    response = client.get(f"/libraries/{lib['id']}/documents/{doc['id']}/chunks")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_chunk(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    chunk = create_chunk_via_api(client, lib["id"], doc["id"], {"text": "Old text"})
    response = client.put(
        f"/libraries/{lib['id']}/documents/{doc['id']}/chunks/{chunk['id']}",
        json={"text": "New text"},
    )
    assert response.status_code == 200
    assert response.json()["text"] == "New text"


def test_update_chunk_partial(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    chunk = create_chunk_via_api(
        client, lib["id"], doc["id"], {"text": "Old", "metadata": {"p": 1}}
    )
    response = client.put(
        f"/libraries/{lib['id']}/documents/{doc['id']}/chunks/{chunk['id']}",
        json={"text": "New"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "New"
    assert data["metadata"] == {"p": 1}


def test_update_chunk_not_found(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    response = client.put(
        f"/libraries/{lib['id']}/documents/{doc['id']}/chunks/{uuid4()}", json={}
    )
    assert response.status_code == 404


def test_delete_chunk(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    chunk = create_chunk_via_api(client, lib["id"], doc["id"], {"text": "to delete"})
    response = client.delete(
        f"/libraries/{lib['id']}/documents/{doc['id']}/chunks/{chunk['id']}"
    )
    assert response.status_code == 204
    assert (
        client.get(
            f"/libraries/{lib['id']}/documents/{doc['id']}/chunks/{chunk['id']}"
        ).status_code
        == 404
    )


# ============================================================================
# RELATIONSHIP & OTHER TESTS (3 tests)
# ============================================================================
def test_library_contains_documents(client):
    lib = create_library_via_api(client)
    doc1 = create_document_via_api(client, lib["id"])
    doc2 = create_document_via_api(client, lib["id"])
    response = client.get(f"/libraries/{lib['id']}")
    data = response.json()
    assert len(data["documents"]) == 2
    assert {doc1["id"], doc2["id"]} == set(data["documents"].keys())


def test_document_contains_chunks(client):
    lib = create_library_via_api(client)
    doc = create_document_via_api(client, lib["id"])
    chunk1 = create_chunk_via_api(client, lib["id"], doc["id"], {"text": "c1"})
    chunk2 = create_chunk_via_api(client, lib["id"], doc["id"], {"text": "c2"})
    response = client.get(f"/libraries/{lib['id']}/documents/{doc['id']}")
    data = response.json()
    assert len(data["chunks"]) == 2
    assert {chunk1["id"], chunk2["id"]} == set(data["chunks"].keys())


def test_invalid_uuid_format(client):
    response = client.get("/libraries/not-a-uuid")
    assert response.status_code == 422
