# vector_db_project/src/api/schemas.py

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from uuid import UUID
from src.core.models import Chunk, Document, Library

# ============================================================================
# CHUNK SCHEMAS
# ============================================================================


class ChunkCreate(BaseModel):
    text: str = Field(..., min_length=1)
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChunkUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChunkResponse(Chunk):
    model_config = {"from_attributes": True}
    id: UUID
    document_id: UUID
    library_id: UUID

    @classmethod
    def from_model(cls, chunk: Chunk, library_id: UUID, document_id: UUID):
        return cls(
            id=chunk.uid,
            document_id=document_id,
            library_id=library_id,
            **chunk.model_dump()
        )


# ============================================================================
# DOCUMENT SCHEMAS
# ============================================================================


class DocumentCreate(BaseModel):
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunks: Optional[List[ChunkCreate]] = None


class DocumentUpdate(BaseModel):
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    library_id: UUID
    metadata: Dict[str, Any]
    chunks: Dict[UUID, Chunk]

    @classmethod
    def from_model(cls, doc: Document, library_id: UUID):
        return cls(id=doc.uid, library_id=library_id, **doc.model_dump(exclude={"uid"}))


# ============================================================================
# LIBRARY SCHEMAS
# ============================================================================


class LibraryCreate(BaseModel):
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LibraryUpdate(BaseModel):
    metadata: Optional[Dict[str, Any]] = None


class LibraryResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    metadata: Dict[str, Any]
    documents: Dict[UUID, Document]

    @classmethod
    def from_model(cls, lib: Library):
        return cls(id=lib.uid, **lib.model_dump(exclude={"uid"}))


# ============================================================================
# SEARCH SCHEMAS
# ============================================================================


class SearchQuery(BaseModel):
    query_embedding: List[float]
    k: int = Field(3, gt=0)


class SearchResult(BaseModel):
    chunk: Chunk
    similarity: float
