# vector_db_project/src/api/endpoints/search.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from src.api import schemas
from src.services.search_service import SearchService
from src.api.dependencies import get_search_service

router = APIRouter()


@router.post(
    "/libraries/{library_id}/search",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.SearchResult],
)
def search_in_library(
    library_id: UUID,
    query: schemas.SearchQuery,
    service: SearchService = Depends(get_search_service),
):
    """
    Performs a k-NN vector search over all chunks in a specific library.
    """
    results = service.search_chunks(
        library_id=library_id,
        query_embedding=query.query_embedding,
        k=query.k,
    )
    return results
