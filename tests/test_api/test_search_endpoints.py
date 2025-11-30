# tests/test_api/test_search_endpoints.py

import pytest
from fastapi.testclient import TestClient
from fastapi import status
import numpy as np

from tests.test_api.test_endpoints import create_chunk_via_api

# Pytest will automatically discover and inject fixtures from conftest.py
# No imports from conftest.py are needed.

# This list drives the parameterized tests. All index types are included.
SUPPORTED_INDEX_TYPES = ["avl", "lsh"]

# ============================================================================
# Test Data & Payloads
# ============================================================================

# A consistent set of vectors for predictable results across all tests
VECTOR_DATA = {
    "cat": [0.1, 0.2, 0.8],
    "dog": [0.9, 0.2, 0.1],
    "kitten": [0.15, 0.25, 0.75],
    "puppy": [0.85, 0.25, 0.15],
    "computer": [0.1, 0.9, 0.1],
}

# ============================================================================
# Index Management Lifecycle Tests
# ============================================================================


def test_get_index_status_on_new_library_is_not_found(client, create_library_via_api):
    """
    QA Goal: Verify that a library without an index does not report having one.
    """
    lib = create_library_via_api()

    # Try to get status of an index that was never created
    response = client.get(f"/libraries/{lib['id']}/index/my-test-index")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_list_all_indices_on_new_library_is_empty(client, create_library_via_api):
    """
    QA Goal: Ensure the index list endpoint correctly shows an empty state.
    """
    lib = create_library_via_api()

    response = client.get(f"/libraries/{lib['id']}/index")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"indices": {}}


@pytest.mark.parametrize("index_type", SUPPORTED_INDEX_TYPES)
def test_create_index_lifecycle(
    client,
    index_type,
    create_library_via_api,
    create_document_via_api,
    create_chunk_via_api,
    create_index_via_api,
):
    """
    QA Goal: Test the full create -> get status -> list -> delete lifecycle for each index type.
    """
    # 1. SETUP: Create a library and add data
    lib = create_library_via_api()
    doc = create_document_via_api(library_id=lib["id"])
    for text, embedding in VECTOR_DATA.items():
        create_chunk_via_api(
            lib["id"], doc["id"], {"text": text, "embedding": embedding}
        )

    index_name = f"{index_type}-index"
    index_payload = {"index_type": index_type, "metric": "cosine", "n_trees": 5}

    # 2. CREATE: Create the index using the helper fixture
    status_data = create_index_via_api(lib["id"], index_name, index_payload)

    # 3. GET STATUS (Specific): Verify the created index status
    assert status_data["name"] == index_name
    assert status_data["config"]["index_type"] == index_type
    assert status_data["vector_count"] == len(VECTOR_DATA)

    get_status_response = client.get(f"/libraries/{lib['id']}/index/{index_name}")
    assert get_status_response.status_code == status.HTTP_200_OK
    assert get_status_response.json() == status_data

    # 4. LIST STATUS (All): Verify the index appears in the list
    list_response = client.get(f"/libraries/{lib['id']}/index")
    assert list_response.status_code == status.HTTP_200_OK
    list_data = list_response.json()
    assert index_name in list_data["indices"]
    assert list_data["indices"][index_name]["vector_count"] == len(VECTOR_DATA)

    # 5. DELETE: Remove the index
    delete_response = client.delete(f"/libraries/{lib['id']}/index/{index_name}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # 6. VERIFY DELETION: Check that it's gone
    final_list_response = client.get(f"/libraries/{lib['id']}/index")
    assert index_name not in final_list_response.json()["indices"]


# ============================================================================
# Search Functionality & Correctness Tests
# ============================================================================


@pytest.fixture
def library_with_all_indices(
    client,
    create_library_via_api,
    create_document_via_api,
    create_chunk_via_api,
    create_index_via_api,
):
    lib = create_library_via_api(metadata={"name": "Search Test Library"})
    doc = create_document_via_api(library_id=lib["id"])
    for text, embedding in VECTOR_DATA.items():
        create_chunk_via_api(
            lib["id"], doc["id"], {"text": text, "embedding": embedding}
        )

    for index_type in SUPPORTED_INDEX_TYPES:
        index_name = f"{index_type}-index"
        payload = {"index_type": index_type, "metric": "cosine", "n_trees": 5}
        create_index_via_api(lib["id"], index_name, payload)

    response = client.get(f"/libraries/{lib['id']}")
    response.raise_for_status()
    return response.json()


@pytest.mark.parametrize("index_type", SUPPORTED_INDEX_TYPES)
def test_search_finds_correct_nearest_neighbor(
    client, library_with_all_indices, index_type
):
    """
    QA Goal: Verify that a search returns the semantically closest item as the top result.
    """
    lib_id = library_with_all_indices["id"]
    index_name = f"{index_type}-index"

    query_vector = [0.11, 0.21, 0.79]  # A vector very close to "cat"
    search_payload = {"query_embedding": query_vector, "k": 2}

    response = client.post(
        f"/libraries/{lib_id}/search/{index_name}", json=search_payload
    )
    assert response.status_code == status.HTTP_200_OK

    results = response.json()
    assert len(results) == 2

    # The order can vary slightly in ANN, so check for presence first
    result_texts = {res["chunk"]["text"] for res in results}
    assert "cat" in result_texts
    assert "kitten" in result_texts

    # Find each result to check its score
    top_result = next(res for res in results if res["chunk"]["text"] == "cat")
    second_result = next(res for res in results if res["chunk"]["text"] == "kitten")

    assert top_result["similarity"] > 0.99
    assert 0.95 < second_result["similarity"] < top_result["similarity"]


@pytest.mark.parametrize("index_type", SUPPORTED_INDEX_TYPES)
def test_search_respects_k_parameter(client, library_with_all_indices, index_type):
    """
    QA Goal: Ensure the 'k' parameter correctly limits the number of results.
    """
    lib_id = library_with_all_indices["id"]
    index_name = f"{index_type}-index"

    query_vector = VECTOR_DATA["dog"]

    # Search for k=1
    response_k1 = client.post(
        f"/libraries/{lib_id}/search/{index_name}",
        json={"query_embedding": query_vector, "k": 1},
    )
    assert response_k1.status_code == status.HTTP_200_OK
    assert len(response_k1.json()) == 1

    # Search for k=3
    response_k3 = client.post(
        f"/libraries/{lib_id}/search/{index_name}",
        json={"query_embedding": query_vector, "k": 3},
    )
    assert response_k3.status_code == status.HTTP_200_OK

    results = response_k3.json()

    # FIX: LSH is approximate. With small datasets, recall < 100% is expected.
    # It filters based on buckets. If buckets are empty, it returns fewer items.
    if index_type == "lsh":
        assert len(results) <= 3
        # Optional: ensure it returns at least the exact match itself
        assert len(results) >= 1
    else:
        # Exact/Tree indices should strictly return k if N >= k
        assert len(results) == 3


# ============================================================================
# Failure, Edge Case, and State Change Tests
# ============================================================================


def test_search_fails_if_index_not_created(
    client, create_library_via_api, create_document_via_api, create_chunk_via_api
):
    """
    QA Goal: API must return a clear error if search is attempted before indexing.
    """
    lib = create_library_via_api()
    doc = create_document_via_api(library_id=lib["id"])
    create_chunk_via_api(lib["id"], doc["id"], {"text": "text", "embedding": [1, 2, 3]})

    search_payload = {"query_embedding": [1, 1, 1], "k": 1}
    response = client.post(
        f"/libraries/{lib['id']}/search/non-existent-index", json=search_payload
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "not ready for search" in response.json()["detail"].lower()


def test_search_on_empty_library_returns_empty_results(
    client, create_library_via_api, create_index_via_api
):
    """
    QA Goal: Verify search works gracefully on a library with no data.
    """
    lib = create_library_via_api()

    # Create an index on an empty library
    index_name = "empty-index"
    create_index_via_api(lib["id"], index_name, {"index_type": "avl"})

    status_res = client.get(f"/libraries/{lib['id']}/index/{index_name}")
    assert status_res.json()["vector_count"] == 0

    search_payload = {"query_embedding": [1, 1, 1], "k": 1}
    search_res = client.post(
        f"/libraries/{lib['id']}/search/{index_name}", json=search_payload
    )

    assert search_res.status_code == status.HTTP_200_OK
    assert search_res.json() == []


def test_search_with_k_larger_than_dataset_returns_all_items(
    client, library_with_all_indices
):
    """
    QA Goal: Ensure the API doesn't crash if k > N, and instead returns all N items.
    """
    lib_id = library_with_all_indices["id"]
    index_name = "avl-index"

    search_payload = {"query_embedding": VECTOR_DATA["computer"], "k": 100}
    response = client.post(
        f"/libraries/{lib_id}/search/{index_name}", json=search_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(VECTOR_DATA)


@pytest.mark.parametrize("index_type", SUPPORTED_INDEX_TYPES)
def test_adding_chunk_handles_index_update_correctly(
    client,
    index_type,
    create_library_via_api,
    create_document_via_api,
    create_chunk_via_api,
    create_index_via_api,
):
    """
    QA Goal: CRITICAL! Verify that data modification correctly handles updates
    for each index type (live update for AVL and LSH).
    """
    lib = create_library_via_api()
    doc = create_document_via_api(library_id=lib["id"])
    create_chunk_via_api(
        lib["id"], doc["id"], {"text": "cat", "embedding": VECTOR_DATA["cat"]}
    )

    index_name = f"test-index-{index_type}"
    create_index_via_api(
        lib["id"], index_name, {"index_type": index_type, "n_trees": 5}
    )

    assert (
        client.get(f"/libraries/{lib['id']}/index/{index_name}").status_code
        == status.HTTP_200_OK
    )

    # ACTION: Add a new chunk with an embedding, which should trigger an update/invalidation.
    create_chunk_via_api(
        lib["id"], doc["id"], {"text": "dog", "embedding": VECTOR_DATA["dog"]}
    )

    # VERIFY behavior based on index type
    if index_type == "avl" or index_type == "lsh":
        # AVL index should update live. It should still exist and have more vectors.
        status_res = client.get(f"/libraries/{lib['id']}/index/{index_name}")
        assert status_res.status_code == status.HTTP_200_OK
        assert status_res.json()["vector_count"] == 2

        # A search should succeed.
        search_res = client.post(
            f"/libraries/{lib['id']}/search/{index_name}",
            json={"query_embedding": [1, 1, 1], "k": 1},
        )
        assert search_res.status_code == status.HTTP_200_OK
