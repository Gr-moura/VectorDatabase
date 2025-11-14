from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4


# ============================================================================
# CHUNK MODELS
# ============================================================================


class ChunkBase(BaseModel):
    """Base model for chunk with required fields."""

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
    """Model for updating an existing chunk - all fields optional."""

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
    """Full chunk model with system-generated fields."""

    uid: UUID = Field(
        alias="id", default_factory=uuid4, description="Unique identifier for the chunk"
    )


# ============================================================================
# DOCUMENT MODELS
# ============================================================================


class DocumentBase(BaseModel):
    """Base model for document with required fields."""

    model_config = {"populate_by_name": True}

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the document"
    )


class DocumentCreate(DocumentBase):
    """Model for creating a new document."""

    pass


class DocumentUpdate(BaseModel):
    """Model for updating an existing document - all fields optional."""

    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the document"
    )


class Document(DocumentBase):
    """Full document model with system-generated fields."""

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
    """Index of library contents for search and retrieval."""

    total_documents: int = 0
    total_chunks: int = 0
    document_names: Dict[UUID, str] = Field(default_factory=dict)
    chunk_texts: Dict[UUID, Dict[UUID, str]] = Field(
        default_factory=dict
    )  # doc_uid -> chunk_uid -> text
    embeddings: Dict[UUID, Dict[UUID, List[float]]] = Field(
        default_factory=dict
    )  # doc_uid -> chunk_uid -> embedding


# ============================================================================
# LIBRARY MODELS
# ============================================================================


class LibraryBase(BaseModel):
    """Base model for library with required fields."""

    name: str = Field(..., min_length=1, description="Name of the library")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for the library"
    )


class LibraryCreate(LibraryBase):
    """Model for creating a new library."""

    pass


class LibraryUpdate(BaseModel):
    """Model for updating an existing library - all fields optional."""

    name: Optional[str] = Field(None, min_length=1, description="Name of the library")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the library"
    )


class Library(LibraryBase):
    """Full library model with system-generated fields."""

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


class ChunkResponse(BaseModel):
    """Response model for chunk operations."""

    chunk: Chunk
    document_uid: UUID
    library_uid: UUID


class DocumentResponse(BaseModel):
    """Response model for document operations."""

    document: Document
    library_uid: UUID


class LibraryResponse(BaseModel):
    """Response model for library operations."""

    library: Library


class IndexResponse(BaseModel):
    """Response model for index operations."""

    library_uid: UUID
    index: LibraryIndex
