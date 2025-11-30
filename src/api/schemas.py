# src/api/schemas.py

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

    index_type: IndexType = Field(
        default=IndexType.AVL,
        description="The type of index to build ('avl' for dynamic exact search, 'lsh' for approximate search).",
    )

    metric: Metric = Field(
        default=Metric.COSINE,
        description="Distance metric for the index (cosine or euclidean).",
    )

    num_bits: int = Field(
        default=8,
        gt=0,
        description="Bits for LSH. More bits = higher precision, lower recall.",
    )

    num_tables: int = Field(
        default=3,
        gt=0,
        description="Tables for LSH. More tables = higher recall, more memory.",
    )

    seed: Optional[int] = Field(
        default=None, description="Random seed for reproducible index creation."
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
# ============================================================================


class ChunkCreate(BaseModel):
    text: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChunkUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class ChunkResponse(BaseModel):
    model_config = API_MODEL_CONFIG
    id: UUID
    document_id: UUID
    library_id: UUID
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any]

    @classmethod
    def from_model(cls, chunk: Chunk, library_id: UUID, document_id: UUID):
        return cls(
            id=chunk.uid,
            document_id=document_id,
            library_id=library_id,
            text=chunk.text,
            embedding=chunk.embedding,
            metadata=chunk.metadata,
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
    chunks: Dict[UUID, ChunkResponse]

    @classmethod
    def from_model(cls, doc: Document, library_id: UUID):
        chunks_response = {
            uid: ChunkResponse.from_model(chunk, library_id, doc.uid)
            for uid, chunk in doc.chunks.items()
        }
        return cls(
            id=doc.uid,
            library_id=library_id,
            metadata=doc.metadata,
            chunks=chunks_response,
        )


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
    documents: Dict[UUID, DocumentResponse]

    @classmethod
    def from_model(cls, lib: Library):
        docs_response = {
            uid: DocumentResponse.from_model(doc, lib.uid)
            for uid, doc in lib.documents.items()
        }
        return cls(id=lib.uid, metadata=lib.metadata, documents=docs_response)


# ============================================================================
# SEARCH SCHEMAS
# ============================================================================


class SearchQuery(BaseModel):
    query_embedding: List[float]
    k: int = Field(3, gt=0)


class SearchResult(BaseModel):
    chunk: ChunkResponse
    similarity: float
