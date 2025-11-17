# vector_db_project/src/core/models.py

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from typing import TYPE_CHECKING

# Import the enums directly, as they are part of the core logic
from src.core.indexing.enums import IndexType, Metric

if TYPE_CHECKING:
    from src.core.indexing.base_index import VectorIndex

# ============================================================================
# INDEX-RELATED CORE MODELS
# ============================================================================


class IndexConfig(BaseModel):
    """
    Core domain model representing the configuration of a vector index.
    This is independent of any API schema.
    """

    index_type: IndexType
    metric: Metric
    # Add other potential config params here as needed


class IndexMetadata(BaseModel):
    """Stores the configuration and state of a built vector index."""

    name: str
    config: IndexConfig
    vector_count: int
    index_type: (
        str  # Slightly redundant with config.index_type but useful for quick lookups
    )


# ============================================================================
# MAIN DOMAIN MODELS
# ============================================================================


class Chunk(BaseModel):
    """Core Chunk model containing text, embedding, and a unique identifier."""

    uid: UUID = Field(default_factory=uuid4)
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    """Core Document model containing chunks and metadata."""

    uid: UUID = Field(default_factory=uuid4)
    chunks: Dict[UUID, Chunk] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Library(BaseModel):
    """Core Library model containing documents, metadata, and multiple named vector indices."""

    model_config = {"arbitrary_types_allowed": True}

    uid: UUID = Field(default_factory=uuid4)
    documents: Dict[UUID, Document] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    indices: Dict[str, "VectorIndex"] = Field(default_factory=dict, exclude=True)
    index_metadata: Dict[str, IndexMetadata] = Field(default_factory=dict)


from src.core.indexing.base_index import VectorIndex

# Rebuild models to resolve the forward reference for VectorIndex
Library.model_rebuild()
