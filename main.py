from typing import List
from uuid import UUID

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse

from services import LibraryService
from schemas import (
    LibraryResponse,
    LibraryCreate,
    LibraryUpdate,
    DocumentResponse,
    DocumentCreate,
    DocumentUpdate,
    ChunkResponse,
    ChunkCreate,
    ChunkUpdate,
)
from exceptions import LibraryNotFound, DocumentNotFound, ChunkNotFound

app = FastAPI()
service = LibraryService()

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================


@app.exception_handler(LibraryNotFound)
async def library_not_found_exception_handler(request: Request, exc: LibraryNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(DocumentNotFound)
async def document_not_found_exception_handler(request: Request, exc: DocumentNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(ChunkNotFound)
async def chunk_not_found_exception_handler(request: Request, exc: ChunkNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/")
def index():
    return {"message": "Welcome to the Library Service API"}


# ============================================================================
# Library Endpoints
# ============================================================================


@app.get(
    "/libraries", status_code=status.HTTP_200_OK, response_model=List[LibraryResponse]
)
def list_libraries():
    return service.list_libraries()


@app.get(
    "/libraries/{library_id}",
    status_code=status.HTTP_200_OK,
    response_model=LibraryResponse,
)
def get_library(library_id: UUID):
    return service.get_library(library_id)


@app.post(
    "/libraries", status_code=status.HTTP_201_CREATED, response_model=LibraryResponse
)
def create_library(library_data: LibraryCreate):
    return service.create_library(library_data)


@app.put(
    "/libraries/{library_id}",
    status_code=status.HTTP_200_OK,
    response_model=LibraryResponse,
)
def update_library(library_id: UUID, library_data: LibraryUpdate):
    return service.update_library(library_id, library_data)


@app.delete("/libraries/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_library(library_id: UUID):
    service.delete_library(library_id)
    return


# ============================================================================
# Document Endpoints
# ============================================================================


@app.get(
    "/libraries/{library_id}/documents",
    status_code=status.HTTP_200_OK,
    response_model=List[DocumentResponse],
)
def list_documents(library_id: UUID):
    documents = service.list_documents(library_id)
    return [{**doc.model_dump(), "library_uid": library_id} for doc in documents]


@app.get(
    "/libraries/{library_id}/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    response_model=DocumentResponse,
)
def get_document(library_id: UUID, document_id: UUID):
    document = service.get_document(library_id, document_id)
    return {**document.model_dump(), "library_uid": library_id}


@app.post(
    "/libraries/{library_id}/documents",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentResponse,
)
def create_document(library_id: UUID, document_data: DocumentCreate):
    document = service.create_document(library_id, document_data)
    return {**document.model_dump(), "library_uid": library_id}


@app.put(
    "/libraries/{library_id}/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    response_model=DocumentResponse,
)
def update_document(library_id: UUID, document_id: UUID, document_data: DocumentUpdate):
    document = service.update_document(library_id, document_id, document_data)
    return {**document.model_dump(), "library_uid": library_id}


@app.delete(
    "/libraries/{library_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(library_id: UUID, document_id: UUID):
    service.delete_document(library_id, document_id)
    return


# ============================================================================
# Chunk Endpoints
# ============================================================================


@app.get(
    "/libraries/{library_id}/documents/{document_id}/chunks",
    status_code=status.HTTP_200_OK,
    response_model=List[ChunkResponse],
)
def list_chunks(library_id: UUID, document_id: UUID):
    chunks = service.list_chunks(library_id, document_id)
    return [
        {**chunk.model_dump(), "library_uid": library_id, "document_uid": document_id}
        for chunk in chunks
    ]


@app.get(
    "/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChunkResponse,
)
def get_chunk(library_id: UUID, document_id: UUID, chunk_id: UUID):
    chunk = service.get_chunk(library_id, document_id, chunk_id)
    return {
        **chunk.model_dump(),
        "library_uid": library_id,
        "document_uid": document_id,
    }


@app.post(
    "/libraries/{library_id}/documents/{document_id}/chunks",
    status_code=status.HTTP_201_CREATED,
    response_model=ChunkResponse,
)
def create_chunk(library_id: UUID, document_id: UUID, chunk_data: ChunkCreate):
    chunk = service.create_chunk(library_id, document_id, chunk_data)
    return {
        **chunk.model_dump(),
        "library_uid": library_id,
        "document_uid": document_id,
    }


@app.put(
    "/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChunkResponse,
)
def update_chunk(
    library_id: UUID, document_id: UUID, chunk_id: UUID, chunk_data: ChunkUpdate
):
    chunk = service.update_chunk(library_id, document_id, chunk_id, chunk_data)
    return {
        **chunk.model_dump(),
        "library_uid": library_id,
        "document_uid": document_id,
    }


@app.delete(
    "/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_chunk(library_id: UUID, document_id: UUID, chunk_id: UUID):
    service.delete_chunk(library_id, document_id, chunk_id)
    return
