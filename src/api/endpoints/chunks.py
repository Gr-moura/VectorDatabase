from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from src.api import schemas
from src.services.chunk_service import ChunkService
from src.api.dependencies import get_chunk_service

router = APIRouter()


@router.post(
    "/libraries/{library_id}/documents/{document_id}/chunks",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ChunkResponse,
)
def create_chunk(
    library_id: UUID,
    document_id: UUID,
    chunk_data: schemas.ChunkCreate,
    service: ChunkService = Depends(get_chunk_service),
):
    chunk = service.create_chunk(library_id, document_id, chunk_data)
    return schemas.ChunkResponse.from_model(chunk, library_id, document_id)


@router.get(
    "/libraries/{library_id}/documents/{document_id}/chunks",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ChunkResponse],
)
def list_chunks(
    library_id: UUID,
    document_id: UUID,
    service: ChunkService = Depends(get_chunk_service),
):
    chunks = service.list_chunks(library_id, document_id)
    return [
        schemas.ChunkResponse.from_model(chunk, library_id, document_id)
        for chunk in chunks
    ]


@router.get(
    "/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ChunkResponse,
)
def get_chunk(
    library_id: UUID,
    document_id: UUID,
    chunk_id: UUID,
    service: ChunkService = Depends(get_chunk_service),
):
    chunk = service.get_chunk(library_id, document_id, chunk_id)
    return schemas.ChunkResponse.from_model(chunk, library_id, document_id)


@router.put(
    "/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ChunkResponse,
)
def update_chunk(
    library_id: UUID,
    document_id: UUID,
    chunk_id: UUID,
    chunk_data: schemas.ChunkUpdate,
    service: ChunkService = Depends(get_chunk_service),
):
    chunk = service.update_chunk(library_id, document_id, chunk_id, chunk_data)
    return schemas.ChunkResponse.from_model(chunk, library_id, document_id)


@router.delete(
    "/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_chunk(
    library_id: UUID,
    document_id: UUID,
    chunk_id: UUID,
    service: ChunkService = Depends(get_chunk_service),
):
    service.delete_chunk(library_id, document_id, chunk_id)
    return
