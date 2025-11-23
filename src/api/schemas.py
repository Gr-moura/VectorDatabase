# vector_db_project/src/api/schemas.py

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from uuid import UUID

# Import core domain models that response schemas will be built FROM
from src.core.models import Chunk, Document, Library, IndexMetadata

# Import core enums that are used in request schemas
from src.core.indexing.enums import IndexType, Metric

API_MODEL_CONFIG = {"from_attributes": True}

# ============================================================================
# INDEX SCHEMAS
# ============================================================================


class IndexCreate(BaseModel):
    """Request model for creating a new vector index."""

    # This is the user's input, so we only include what they can control.
    index_type: IndexType = Field(
        default=IndexType.AVL,
        description="The type of index to build ('avl' for dynamic exact search).",
    )
    metric: Metric = Field(
        default=Metric.COSINE,
        description="Distance metric for the index (cosine or euclidean).",
    )


class IndexConfigResponse(BaseModel):
    """Schema for the 'config' part of an index status response."""

    model_config = API_MODEL_CONFIG
    index_type: IndexType
    metric: Metric


class IndexStatusResponse(BaseModel):
    """Response model for the status of a specific index."""

    model_config = API_MODEL_CONFIG
    name: str
    config: IndexConfigResponse  # Use the dedicated response schema
    vector_count: int
    index_type: str


class AllIndicesStatusResponse(BaseModel):
    """Response model for the status of all indices in a library."""

    model_config = API_MODEL_CONFIG
    indices: Dict[str, IndexStatusResponse]


# ============================================================================
# CHUNK SCHEMAS
# ===========================================================================


class ChunkCreate(BaseModel):
    text: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChunkUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class ChunkResponse(Chunk):
    model_config = API_MODEL_CONFIG
    id: UUID
    document_id: UUID
    library_id: UUID

    @classmethod
    def from_model(cls, chunk: Chunk, library_id: UUID, document_id: UUID):
        return cls(
            id=chunk.uid,
            document_id=document_id,
            library_id=library_id,
            **chunk.model_dump(exclude={"uid"}),
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
    model_config = API_MODEL_CONFIG
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
    model_config = API_MODEL_CONFIG
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
    """Request model for a vector search query."""

    query_embedding: List[float] = Field(
        ..., description="The embedding vector for the query."
    )
    k: int = Field(3, gt=0, description="The number of nearest neighbors to return.")


class SearchResult(BaseModel):
    """Response model for a single search result item."""

    chunk: Chunk
    similarity: float = Field(
        ...,
        description="The search score. For cosine, higher is better. For euclidean, lower is better.",
    )
