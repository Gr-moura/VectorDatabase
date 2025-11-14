# tests/test_api.py
import uuid
from typing import Any, Dict, List
import pytest
from fastapi.testclient import TestClient

# Adjust this import if your FastAPI file has a different name (e.g., api.py)
import main


class DummyService:
    """
    A small, configurable fake service to replace the real `service` used by the FastAPI app.
    Each attribute corresponds to a method used by the API and should be set to the desired return value.
    If a method needs to be callable (e.g. to assert it was called), replace the attribute with a callable.
    """

    def __init__(self):
        # library-related
        self.list_libraries_return = None
        self.get_library_return = None
        self.create_library_return = None
        self.update_library_return = None
        self.delete_library_return = None

        # document-related
        self.list_documents_return = None
        self.get_document_return = None
        self.create_document_return = None
        self.update_document_return = None
        self.delete_document_return = None

        # chunk-related
        self.list_chunks_return = None
        self.get_chunk_return = None
        self.create_chunk_return = None
        self.update_chunk_return = None
        self.delete_chunk_return = None

    # Library methods
    def list_libraries(self):
        return self.list_libraries_return

    def get_library(self, library_id):
        return self.get_library_return

    def create_library(self, library_data):
        return self.create_library_return

    def update_library(self, library_id, library_data):
        return self.update_library_return

    def delete_library(self, library_id):
        return self.delete_library_return

    # Document methods
    def list_documents(self, library_id):
        return self.list_documents_return

    def get_document(self, library_id, document_id):
        return self.get_document_return

    def create_document(self, library_id, document_data):
        return self.create_document_return

    def update_document(self, library_id, document_id, document_data):
        return self.update_document_return

    def delete_document(self, library_id, document_id):
        return self.delete_document_return

    # Chunk methods
    def list_chunks(self, library_id, document_id):
        return self.list_chunks_return

    def get_chunk(self, library_id, document_id, chunk_id):
        return self.get_chunk_return

    def create_chunk(self, library_id, document_id, chunk_data):
        return self.create_chunk_return

    def update_chunk(self, library_id, document_id, chunk_id, chunk_data):
        return self.update_chunk_return

    def delete_chunk(self, library_id, document_id, chunk_id):
        return self.delete_chunk_return


@pytest.fixture(autouse=True)
def client_and_service(monkeypatch) -> TestClient:
    """
    Fixture that creates a TestClient and monkeypatches main.service to a fresh DummyService for each test.
    Tests can mutate `main.service` to control behavior.
    """
    dummy = DummyService()
    monkeypatch.setattr(main, "service", dummy, raising=False)
    client = TestClient(main.app)
    return client


def test_index_route(client_and_service):
    resp = client_and_service.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Welcome to the Library Service API"}


# --------------------
# Libraries
# --------------------
def test_list_libraries_not_found(client_and_service):
    # service.list_libraries returns falsy => 404
    main.service.list_libraries_return = []
    resp = client_and_service.get("/libraries")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No libraries found"


def test_list_libraries_success(client_and_service):
    lib = {"id": str(uuid.uuid4()), "name": "lib1"}
    main.service.list_libraries_return = [lib]
    resp = client_and_service.get("/libraries")
    assert resp.status_code == 200
    body = resp.json()
    assert "libraries" in body
    assert body["libraries"][0]["id"] == lib["id"]


def test_get_library_not_found(client_and_service):
    main.service.get_library_return = None
    lib_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Library not found"


def test_get_library_success(client_and_service):
    lib = {"id": str(uuid.uuid4()), "name": "libX"}
    main.service.get_library_return = lib
    resp = client_and_service.get(f"/libraries/{lib['id']}")
    assert resp.status_code == 200
    assert resp.json()["library"]["id"] == lib["id"]


def test_create_library(client_and_service):
    payload = {"name": "new lib"}
    created = {"id": str(uuid.uuid4()), "name": payload["name"]}
    main.service.create_library_return = created
    resp = client_and_service.post("/libraries", json=payload)
    assert resp.status_code == 201
    assert resp.json()["library"]["name"] == payload["name"]
    assert resp.json()["library"]["id"] == created["id"]


def test_update_library_not_found(client_and_service):
    main.service.update_library_return = None
    lib_id = str(uuid.uuid4())
    resp = client_and_service.put(f"/libraries/{lib_id}", json={"name": "x"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Library not found"


def test_update_library_success(client_and_service):
    lib_id = str(uuid.uuid4())
    updated = {"id": lib_id, "name": "updated name"}
    main.service.update_library_return = updated
    resp = client_and_service.put(
        f"/libraries/{lib_id}", json={"name": updated["name"]}
    )
    assert resp.status_code == 200
    assert resp.json()["library"]["name"] == "updated name"


def test_delete_library_not_found(client_and_service):
    main.service.delete_library_return = False
    lib_id = str(uuid.uuid4())
    resp = client_and_service.delete(f"/libraries/{lib_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Library not found"


def test_delete_library_success(client_and_service):
    main.service.delete_library_return = True
    lib_id = str(uuid.uuid4())
    resp = client_and_service.delete(f"/libraries/{lib_id}")
    # The app sets status_code=status.HTTP_204_NO_CONTENT; check status code
    assert resp.status_code == 204
    # if body included, verify message; otherwise allow empty body
    if resp.content:
        assert resp.json()["detail"] == "Library deleted successfully"


# --------------------
# Documents
# --------------------
def test_list_documents_not_found(client_and_service):
    main.service.list_documents_return = []
    lib_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No documents found"


def test_list_documents_success(client_and_service):
    doc = {"id": str(uuid.uuid4()), "title": "doc1"}
    main.service.list_documents_return = [doc]
    lib_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents")
    assert resp.status_code == 200
    assert resp.json()["documents"][0]["id"] == doc["id"]


def test_get_document_not_found(client_and_service):
    main.service.get_document_return = None
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Document not found"


def test_get_document_success(client_and_service):
    doc = {"id": str(uuid.uuid4()), "title": "docX"}
    main.service.get_document_return = doc
    lib_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc['id']}")
    assert resp.status_code == 200
    assert resp.json()["document"]["id"] == doc["id"]


def test_create_document_library_not_found(client_and_service):
    main.service.create_document_return = None
    lib_id = str(uuid.uuid4())
    payload = {"title": "a doc"}
    resp = client_and_service.post(f"/libraries/{lib_id}/documents", json=payload)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Library not found"


def test_create_document_success(client_and_service):
    lib_id = str(uuid.uuid4())
    created_doc = {"id": str(uuid.uuid4()), "title": "created"}
    main.service.create_document_return = created_doc
    resp = client_and_service.post(
        f"/libraries/{lib_id}/documents", json={"title": created_doc["title"]}
    )
    assert resp.status_code == 201
    assert resp.json()["document"]["id"] == created_doc["id"]


def test_update_document_not_found(client_and_service):
    main.service.update_document_return = None
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.put(
        f"/libraries/{lib_id}/documents/{doc_id}", json={"title": "x"}
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Document not found"


def test_update_document_success(client_and_service):
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    updated = {"id": doc_id, "title": "updated"}
    main.service.update_document_return = updated
    resp = client_and_service.put(
        f"/libraries/{lib_id}/documents/{doc_id}", json={"title": updated["title"]}
    )
    assert resp.status_code == 200
    assert resp.json()["document"]["title"] == "updated"


def test_delete_document_not_found(client_and_service):
    main.service.delete_document_return = False
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.delete(f"/libraries/{lib_id}/documents/{doc_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Document not found"


def test_delete_document_success(client_and_service):
    main.service.delete_document_return = True
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.delete(f"/libraries/{lib_id}/documents/{doc_id}")
    assert resp.status_code == 204
    if resp.content:
        assert resp.json()["detail"] == "Document deleted successfully"


# --------------------
# Chunks
# --------------------
def test_list_chunks_not_found(client_and_service):
    main.service.list_chunks_return = []
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc_id}/chunks")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No chunks found"


def test_list_chunks_success(client_and_service):
    chunk = {"id": str(uuid.uuid4()), "text": "c"}
    main.service.list_chunks_return = [chunk]
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc_id}/chunks")
    assert resp.status_code == 200
    assert resp.json()["chunks"][0]["id"] == chunk["id"]


def test_get_chunk_not_found(client_and_service):
    main.service.get_chunk_return = None
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())
    resp = client_and_service.get(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk_id}"
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Chunk not found"


def test_get_chunk_success(client_and_service):
    chunk = {"id": str(uuid.uuid4()), "text": "chunk"}
    main.service.get_chunk_return = chunk
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.get(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk['id']}"
    )
    assert resp.status_code == 200
    assert resp.json()["chunk"]["id"] == chunk["id"]


def test_create_chunk_document_not_found(client_and_service):
    main.service.create_chunk_return = None
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.post(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks", json={"text": "x"}
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Document not found"


def test_create_chunk_success(client_and_service):
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    created = {"id": str(uuid.uuid4()), "text": "created"}
    main.service.create_chunk_return = created
    resp = client_and_service.post(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks", json={"text": created["text"]}
    )
    assert resp.status_code == 201
    assert resp.json()["chunk"]["id"] == created["id"]


def test_update_chunk_not_found(client_and_service):
    main.service.update_chunk_return = None
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())
    resp = client_and_service.put(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk_id}", json={"text": "x"}
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Chunk not found"


def test_update_chunk_success(client_and_service):
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())
    updated = {"id": chunk_id, "text": "updated"}
    main.service.update_chunk_return = updated
    resp = client_and_service.put(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk_id}",
        json={"text": "updated"},
    )
    assert resp.status_code == 200
    assert resp.json()["chunk"]["text"] == "updated"


def test_delete_chunk_not_found(client_and_service):
    main.service.delete_chunk_return = False
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())
    resp = client_and_service.delete(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk_id}"
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Chunk not found"


def test_delete_chunk_success(client_and_service):
    main.service.delete_chunk_return = True
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    chunk_id = str(uuid.uuid4())
    resp = client_and_service.delete(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk_id}"
    )
    assert resp.status_code == 204
    if resp.content:
        assert resp.json()["detail"] == "Chunk deleted successfully"
