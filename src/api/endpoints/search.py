# src/api/endpoints/search.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response

from src.api import schemas
from src.services.search_service import SearchService
from src.api.dependencies import get_search_service

router = APIRouter()


@router.post(
    "/libraries/{library_id}/index/{index_name}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.IndexStatusResponse,
)
def create_library_index(
    library_id: UUID,
    index_name: str,
    index_config: schemas.IndexCreate,
    response: Response,
    service: SearchService = Depends(get_search_service),
):
    """
    Creates (or recreates) a named vector index for a library.

    - **index_type**: 'avl' is currently supported.
    - **metric**: 'cosine' (default) or 'euclidean'.
    """
    service.create_index(library_id, index_name, index_config)

    response.headers["Location"] = f"/libraries/{library_id}/index/{index_name}"

    return service.get_index_status(library_id, index_name)


@router.get(
    "/libraries/{library_id}/index/{index_name}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.IndexStatusResponse,
)
def get_library_index_status(
    library_id: UUID,
    index_name: str,
    service: SearchService = Depends(get_search_service),
):
    """Retrieves the status of a specific named vector index."""
    return service.get_index_status(library_id, index_name)


@router.delete(
    "/libraries/{library_id}/index/{index_name}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_library_index(
    library_id: UUID,
    index_name: str,
    service: SearchService = Depends(get_search_service),
):
    """Deletes a named vector index from a library."""
    service.delete_index(library_id, index_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================================================
# General paths (without {index_name}) come after specific ones.
# ============================================================================


@router.get(
    "/libraries/{library_id}/index",
    status_code=status.HTTP_200_OK,
    response_model=schemas.AllIndicesStatusResponse,
)
def list_all_library_indices(
    library_id: UUID, service: SearchService = Depends(get_search_service)
):
    """Lists all available indices and their metadata for a given library."""
    indices_metadata = service.list_all_indices(library_id)
    return schemas.AllIndicesStatusResponse(indices=indices_metadata)


# ============================================================================
# Search Endpoint
# ============================================================================


@router.post(
    "/libraries/{library_id}/search/{index_name}",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.SearchResult],
)
def search_in_library(
    library_id: UUID,
    index_name: str,
    query: schemas.SearchQuery,
    service: SearchService = Depends(get_search_service),
):
    """
    Performs a k-NN vector search using a specific named index.
    You can provide either 'query_embedding' (raw vector) or 'query_text' (to be embedded by the backend).
    """
    results = service.search_chunks(
        library_id=library_id,
        index_name=index_name,
        query_embedding=query.query_embedding,
        k=query.k,
        query_text=query.query_text,
    )
    return results
