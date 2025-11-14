from services import *
from schemas import *
from fastapi import FastAPI, status, HTTPException

app = FastAPI()
service = LibraryService()


@app.get("/")
def index():
    return {"message": "Welcome to the Library Service API"}


# ============================================================================
# Library Endpoints
# ============================================================================


# Read all libraries
@app.get(
    "/libraries", status_code=status.HTTP_200_OK, response_model=List[LibraryResponse]
)
def list_libraries():
    libraries = service.list_libraries()

    if not libraries:
        raise HTTPException(status_code=404, detail="No libraries found")

    return {"libraries": libraries}


# Read a specific library
@app.get(
    "/libraries/{library_id}",
    status_code=status.HTTP_200_OK,
    response_model=LibraryResponse,
)
def get_library(library_id: UUID):
    library = service.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return {"library": library}


# Create a new library
@app.post(
    "/libraries", status_code=status.HTTP_201_CREATED, response_model=LibraryResponse
)
def create_library(library_data: LibraryCreate):
    library = service.create_library(library_data)
    return {"library": library}


# Update an existing library
@app.put(
    "/libraries/{library_id}",
    status_code=status.HTTP_200_OK,
    response_model=LibraryResponse,
)
def update_library(library_id: UUID, library_data: LibraryUpdate):
    library = service.update_library(library_id, library_data)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return {"library": library}


# Delete a library
@app.delete("/libraries/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_library(library_id: UUID):
    success = service.delete_library(library_id)
    if not success:
        raise HTTPException(status_code=404, detail="Library not found")
    return {"detail": "Library deleted successfully"}


# ============================================================================
# Document Endpoints
# ============================================================================


# Read all documents in a library
@app.get(
    "/libraries/{library_id}/documents",
    status_code=status.HTTP_200_OK,
    response_model=List[DocumentResponse],
)
def list_documents(library_id: UUID):
    documents = service.list_documents(library_id)
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found")
    return {"documents": documents}


# Read a specific document
@app.get(
    "/libraries/{library_id}/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    response_model=DocumentResponse,
)
def get_document(library_id: UUID, document_id: UUID):
    document_data = service.get_document(library_id, document_id)
    if not document_data:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document": document_data}


# Create a new document in a library
@app.post(
    "/libraries/{library_id}/documents",
    status_code=status.HTTP_201_CREATED,
    response_model=DocumentResponse,
)
def create_document(library_id: UUID, document_data: DocumentCreate):
    document = service.create_document(library_id, document_data)
    if not document:
        raise HTTPException(status_code=404, detail="Library not found")
    return {"document": document}


# Update an existing document
@app.put(
    "/libraries/{library_id}/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    response_model=DocumentResponse,
)
def update_document(library_id: UUID, document_id: UUID, document_data: DocumentUpdate):
    document = service.update_document(library_id, document_id, document_data)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document": document}


# Delete a document
@app.delete(
    "/libraries/{library_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(library_id: UUID, document_id: UUID):
    success = service.delete_document(library_id, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"detail": "Document deleted successfully"}


# ============================================================================
# Chunk Endpoints
# ============================================================================


# Read all chunks in a document
@app.get(
    "/libraries/{library_id}/documents/{document_id}/chunks",
    status_code=status.HTTP_200_OK,
    response_model=List[ChunkResponse],
)
def list_chunks(library_id: UUID, document_id: UUID):
    chunks = service.list_chunks(library_id, document_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found")
    return {"chunks": chunks}


# Read a specific chunk
@app.get(
    "/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChunkResponse,
)
def get_chunk(library_id: UUID, document_id: UUID, chunk_id: UUID):
    chunk_data = service.get_chunk(library_id, document_id, chunk_id)
    if not chunk_data:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {"chunk": chunk_data}


# Create a new chunk in a document
@app.post(
    "/libraries/{library_id}/documents/{document_id}/chunks",
    status_code=status.HTTP_201_CREATED,
    response_model=ChunkResponse,
)
def create_chunk(library_id: UUID, document_id: UUID, chunk_data: ChunkCreate):
    chunk = service.create_chunk(library_id, document_id, chunk_data)
    if not chunk:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"chunk": chunk}


# Update an existing chunk
@app.put(
    "/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_200_OK,
    response_model=ChunkResponse,
)
def update_chunk(
    library_id: UUID, document_id: UUID, chunk_id: UUID, chunk_data: ChunkUpdate
):
    chunk = service.update_chunk(library_id, document_id, chunk_id, chunk_data)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {"chunk": chunk}


# Delete a chunk
@app.delete(
    "/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_chunk(library_id: UUID, document_id: UUID, chunk_id: UUID):
    success = service.delete_chunk(library_id, document_id, chunk_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {"detail": "Chunk deleted successfully"}
