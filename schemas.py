from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4


# ============================================================================
# CHUNK MODELS
# ============================================================================


class ChunkBase(BaseModel):
    text: str = Field(..., min_length=1, description="The text content of the chunk")
    embedding: Optional[List[float]] = Field(
        None, description="Vector embedding of the chunk"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the chunk"
    )


class ChunkCreate(ChunkBase):
    pass


class ChunkUpdate(BaseModel):
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
    model_config = {"populate_by_name": True}
    uid: UUID = Field(
        alias="id", default_factory=uuid4, description="Unique identifier for the chunk"
    )


# ============================================================================
# DOCUMENT MODELS
# ============================================================================


class DocumentBase(BaseModel):
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the document"
    )


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the document"
    )


class Document(DocumentBase):
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
# LIBRARY INDEX MODEL
# ============================================================================


class LibraryIndex(BaseModel):
    total_documents: int = 0
    total_chunks: int = 0
    document_names: Dict[UUID, str] = Field(default_factory=dict)
    chunk_texts: Dict[UUID, Dict[UUID, str]] = Field(default_factory=dict)
    embeddings: Dict[UUID, Dict[UUID, List[float]]] = Field(default_factory=dict)


# ============================================================================
# LIBRARY MODELS
# ============================================================================


class LibraryBase(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the library")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the library"
    )


class LibraryCreate(LibraryBase):
    pass


class LibraryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Name of the library")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the library"
    )


class Library(LibraryBase):
    model_config = {"populate_by_name": True}
    uid: UUID = Field(
        alias="id",
        default_factory=uuid4,
        description="Unique identifier for the library",
    )
    documents: Dict[UUID, Document] = Field(
        default_factory=dict, description="Dictionary of documents indexed by UID"
    )
    index: Optional[LibraryIndex] = Field(
        None, description="Search index for the library contents"
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


class IndexResponse(BaseModel):
    library_uid: UUID
    index: LibraryIndex
