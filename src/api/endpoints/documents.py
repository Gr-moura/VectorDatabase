# src/api/endpoints/documents.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Response, status
from src.api import schemas
from src.services.document_service import DocumentService
from src.api.dependencies import get_document_service

router = APIRouter()


@router.post(
    "/libraries/{library_id}/documents",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.DocumentResponse,
)
def create_document(
    library_id: UUID,
    document_data: schemas.DocumentCreate,
    response: Response,
    service: DocumentService = Depends(get_document_service),
):
    document = service.create_document(library_id, document_data)
    response.headers["Location"] = f"/libraries/{library_id}/documents/{document.uid}"
    return schemas.DocumentResponse.from_model(document, library_id)


@router.get(
    "/libraries/{library_id}/documents",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.DocumentResponse],
)
def list_documents(
    library_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    documents = service.list_documents(library_id)
    return [schemas.DocumentResponse.from_model(doc, library_id) for doc in documents]


@router.get(
    "/libraries/{library_id}/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.DocumentResponse,
)
def get_document(
    library_id: UUID,
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    document = service.get_document(library_id, document_id)
    return schemas.DocumentResponse.from_model(document, library_id)


@router.put(
    "/libraries/{library_id}/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.DocumentResponse,
)
def update_document(
    library_id: UUID,
    document_id: UUID,
    document_data: schemas.DocumentUpdate,
    service: DocumentService = Depends(get_document_service),
):
    document = service.update_document(library_id, document_id, document_data)
    return schemas.DocumentResponse.from_model(document, library_id)


@router.delete(
    "/libraries/{library_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    library_id: UUID,
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    service.delete_document(library_id, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
