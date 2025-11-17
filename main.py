# vector_db_project/main.py

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.endpoints import libraries, documents, chunks, search
from src.core.exceptions import (
    LibraryNotFound,
    DocumentNotFound,
    ChunkNotFound,
    IndexNotReady,
)

# Create the main FastAPI application
app = FastAPI(
    title="Vector DB Project",
    description="A simple vector database API using FastAPI",
    version="1.0.0",
)

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================


@app.exception_handler(IndexNotReady)
async def index_not_ready_exception_handler(request: Request, exc: IndexNotReady):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,  # 409 Conflict is a good choice here
        content={"detail": str(exc)},
    )


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
# API Routers
# ============================================================================

# Include routers from the API layer. This keeps the main file organized.
app.include_router(libraries.router, prefix="/libraries", tags=["Libraries"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(chunks.router, tags=["Chunks"])
app.include_router(search.router, tags=["Search"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Vector DB API"}


# Optional: Add a main block to run the app with uvicorn for easy development
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
