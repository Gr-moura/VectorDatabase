# tests/test_api/conftest.py

import pytest
from uuid import UUID, uuid4
from typing import Dict, Any, Optional, Generator
from fastapi.testclient import TestClient

from main import app
from src.api.dependencies import library_repository

# ============================================================================
# Core Pytest Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, Any, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_repository() -> Generator[None, Any, None]:
    library_repository.clear()
    yield
    library_repository.clear()


# ============================================================================
# API Helper Fixtures (Factories)
# ============================================================================


@pytest.fixture(scope="session")
def create_library_via_api(client: TestClient):
    """A factory fixture to create a library. Returns a function."""

    def _create_library(metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if metadata is None:
            metadata = {"name": f"Test Library {uuid4()}"}
        response = client.post("/libraries/", json={"metadata": metadata})
        response.raise_for_status()
        return response.json()

    return _create_library


@pytest.fixture(scope="session")
def create_document_via_api(client: TestClient):
    """A factory fixture to create a document. Returns a function."""

    def _create_document(
        library_id: UUID, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if metadata is None:
            metadata = {"title": f"Test Document {uuid4()}"}
        url = f"/libraries/{library_id}/documents"
        response = client.post(url, json={"metadata": metadata})
        response.raise_for_status()
        return response.json()

    return _create_document


@pytest.fixture(scope="session")
def create_chunk_via_api(client: TestClient):
    """A factory fixture to create a chunk. Returns a function."""

    def _create_chunk(
        library_id: UUID, document_id: UUID, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        url = f"/libraries/{library_id}/documents/{document_id}/chunks"
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    return _create_chunk


@pytest.fixture(scope="session")
def create_index_via_api(client: TestClient):
    """A factory fixture to create an index. Returns a function."""

    def _create_index(
        library_id: UUID, index_name: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        url = f"/libraries/{library_id}/index/{index_name}"
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    return _create_index
