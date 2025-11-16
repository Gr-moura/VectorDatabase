# vector_db_project/src/api/endpoints/libraries.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from src.api import schemas
from src.services.library_service import LibraryService
from src.api.dependencies import get_library_service

router = APIRouter()


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.LibraryResponse
)
def create_library(
    library_data: schemas.LibraryCreate,
    service: LibraryService = Depends(get_library_service),
):
    library = service.create_library(library_data)
    return schemas.LibraryResponse.from_model(library)


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[schemas.LibraryResponse]
)
def list_libraries(service: LibraryService = Depends(get_library_service)):
    libraries = service.list_libraries()
    return [schemas.LibraryResponse.from_model(lib) for lib in libraries]


@router.get(
    "/{library_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LibraryResponse,
)
def get_library(
    library_id: UUID, service: LibraryService = Depends(get_library_service)
):
    library = service.get_library(library_id)
    return schemas.LibraryResponse.from_model(library)


@router.put(
    "/{library_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LibraryResponse,
)
def update_library(
    library_id: UUID,
    library_data: schemas.LibraryUpdate,
    service: LibraryService = Depends(get_library_service),
):
    library = service.update_library(library_id, library_data)
    return schemas.LibraryResponse.from_model(library)


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_library(
    library_id: UUID, service: LibraryService = Depends(get_library_service)
):
    service.delete_library(library_id)
    return
