from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4


# ============================================================================
# CHUNK MODELS
# ============================================================================


class ChunkBase(BaseModel):
    """Base model for a chunk, including text, embedding, and metadata."""

    text: str = Field(..., min_length=1, description="The text content of the chunk")
    embedding: Optional[List[float]] = Field(
        None, description="Vector embedding of the chunk"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the chunk"
    )


class ChunkCreate(ChunkBase):
    """Model for creating a new chunk."""

    pass


class ChunkUpdate(BaseModel):
    """Model for updating an existing chunk."""

    text: Optional[str] = Field(
        None, min_length=1, description="The text content of the chunk"
    )
    embedding: Optional[List[float]] = Field(
        None, description="Vector embedding of the chunk"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the chunk"
    )


class Chunk(ChunkBase):
    """Chunk model containing text, embedding, metadata, and a unique identifier."""

    model_config = {"populate_by_name": True}
    uid: UUID = Field(
        alias="id", default_factory=uuid4, description="Unique identifier for the chunk"
    )


# ============================================================================
# DOCUMENT MODELS
# ============================================================================


class DocumentBase(BaseModel):
    """Base model for a document, including metadata."""

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the document"
    )


class DocumentCreate(DocumentBase):
    """Model for creating a new document."""

    pass


class DocumentUpdate(BaseModel):
    """Model for updating an existing document."""

    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the document"
    )


class Document(DocumentBase):
    """Document model containing chunks and metadata."""

    model_config = {"populate_by_name": True}
    uid: UUID = Field(
        alias="id",
        default_factory=uuid4,
        description="Unique identifier for the document",
    )
    chunks: Dict[UUID, Chunk] = Field(
        default_factory=dict, description="Dictionary of chunks indexed by UID"
    )


# ============================================================================
# LIBRARY MODELS
# ============================================================================


class LibraryBase(BaseModel):
    """Base model for a library, including metadata."""

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the library"
    )


class LibraryCreate(LibraryBase):
    """Model for creating a new library."""

    pass


class LibraryUpdate(BaseModel):
    """Model for updating an existing library."""

    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the library"
    )


class Library(LibraryBase):
    """Library model containing documents and metadata."""

    model_config = {"populate_by_name": True}
    uid: UUID = Field(
        alias="id",
        default_factory=uuid4,
        description="Unique identifier for the library",
    )
    documents: Dict[UUID, Document] = Field(
        default_factory=dict, description="Dictionary of documents indexed by UID"
    )


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class ChunkResponse(Chunk):
    """Response model for a chunk, including parent IDs."""

    document_uid: UUID
    library_uid: UUID


class DocumentResponse(Document):
    """Response model for a document, including its parent library ID."""

    library_uid: UUID


LibraryResponse = Library


# ============================================================================
# SEARCH MODELS
# ============================================================================


class SearchQuery(BaseModel):
    """Request model for a vector search query."""

    query_embedding: List[float] = Field(
        ..., description="The embedding vector to search for."
    )
    k: int = Field(
        default=3, gt=0, description="The number of nearest neighbors to return."
    )


class SearchResult(BaseModel):
    """Response model for a single search result item."""

    chunk: Chunk
    similarity: float = Field(
        ..., description="The cosine similarity score of the result (higher is better)."
    )
