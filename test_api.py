# tests/test_api.py
import uuid
from typing import Any, Dict, List
import pytest
from fastapi.testclient import TestClient

import main


class DummyService:

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
    lib = {"id": str(uuid.uuid4()), "name": "lib1", "metadata": {}, "documents": {}}
    main.service.list_libraries_return = [lib]
    resp = client_and_service.get("/libraries")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert body[0]["id"] == lib["id"]


def test_get_library_not_found(client_and_service):
    main.service.get_library_return = None
    lib_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Library not found"


def test_get_library_success(client_and_service):
    lib = {"id": str(uuid.uuid4()), "name": "libX", "metadata": {}, "documents": {}}
    main.service.get_library_return = lib
    resp = client_and_service.get(f"/libraries/{lib['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == lib["id"]


def test_create_library(client_and_service):
    payload = {"name": "new lib"}
    created = {
        "id": str(uuid.uuid4()),
        "name": payload["name"],
        "metadata": {},
        "documents": {},
    }
    main.service.create_library_return = created
    resp = client_and_service.post("/libraries", json=payload)
    assert resp.status_code == 201
    assert resp.json()["name"] == payload["name"]
    assert resp.json()["id"] == created["id"]


def test_update_library_not_found(client_and_service):
    main.service.update_library_return = None
    lib_id = str(uuid.uuid4())
    resp = client_and_service.put(f"/libraries/{lib_id}", json={"name": "x"})
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Library not found"


def test_update_library_success(client_and_service):
    lib_id = str(uuid.uuid4())
    updated = {"id": lib_id, "name": "updated name", "metadata": {}, "documents": {}}
    main.service.update_library_return = updated
    resp = client_and_service.put(
        f"/libraries/{lib_id}", json={"name": updated["name"]}
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "updated name"


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
    assert resp.status_code == 204
    assert not resp.content


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
    doc = {"id": str(uuid.uuid4()), "metadata": {}, "chunks": {}}
    main.service.list_documents_return = [doc]
    lib_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert body[0]["id"] == doc["id"]
    assert body[0]["library_uid"] == lib_id


def test_get_document_not_found(client_and_service):
    main.service.get_document_return = None
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Document not found"


def test_get_document_success(client_and_service):
    doc = {"id": str(uuid.uuid4()), "metadata": {}, "chunks": {}}
    main.service.get_document_return = doc
    lib_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == doc["id"]
    assert resp.json()["library_uid"] == lib_id


def test_create_document_library_not_found(client_and_service):
    main.service.create_document_return = None
    lib_id = str(uuid.uuid4())
    payload = {"metadata": {}}
    resp = client_and_service.post(f"/libraries/{lib_id}/documents", json=payload)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Library not found"


def test_create_document_success(client_and_service):
    lib_id = str(uuid.uuid4())
    created_doc = {"id": str(uuid.uuid4()), "metadata": {}, "chunks": {}}
    main.service.create_document_return = created_doc
    resp = client_and_service.post(
        f"/libraries/{lib_id}/documents", json={"metadata": {}}
    )
    assert resp.status_code == 201
    assert resp.json()["id"] == created_doc["id"]
    assert resp.json()["library_uid"] == lib_id


def test_update_document_not_found(client_and_service):
    main.service.update_document_return = None
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.put(
        f"/libraries/{lib_id}/documents/{doc_id}", json={"metadata": {"key": "val"}}
    )
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Document not found"


def test_update_document_success(client_and_service):
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    updated = {"id": doc_id, "metadata": {"status": "updated"}, "chunks": {}}
    main.service.update_document_return = updated
    resp = client_and_service.put(
        f"/libraries/{lib_id}/documents/{doc_id}",
        json={"metadata": updated["metadata"]},
    )
    assert resp.status_code == 200
    assert resp.json()["metadata"]["status"] == "updated"


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
    assert not resp.content


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
    chunk = {"id": str(uuid.uuid4()), "text": "c", "metadata": {}}
    main.service.list_chunks_return = [chunk]
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc_id}/chunks")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert body[0]["id"] == chunk["id"]
    assert body[0]["library_uid"] == lib_id
    assert body[0]["document_uid"] == doc_id


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
    chunk = {"id": str(uuid.uuid4()), "text": "chunk", "metadata": {}}
    main.service.get_chunk_return = chunk
    lib_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    resp = client_and_service.get(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk['id']}"
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == chunk["id"]
    assert resp.json()["library_uid"] == lib_id
    assert resp.json()["document_uid"] == doc_id


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
    created = {"id": str(uuid.uuid4()), "text": "created", "metadata": {}}
    main.service.create_chunk_return = created
    resp = client_and_service.post(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks", json={"text": created["text"]}
    )
    assert resp.status_code == 201
    assert resp.json()["id"] == created["id"]
    assert resp.json()["library_uid"] == lib_id
    assert resp.json()["document_uid"] == doc_id


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
    updated = {"id": chunk_id, "text": "updated", "metadata": {}}
    main.service.update_chunk_return = updated
    resp = client_and_service.put(
        f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk_id}",
        json={"text": "updated"},
    )
    assert resp.status_code == 200
    assert resp.json()["text"] == "updated"


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
    assert not resp.content
