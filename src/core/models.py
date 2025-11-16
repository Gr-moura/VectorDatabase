# vector_db_project/src/core/models.py

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4


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
    """Core Library model containing documents and metadata."""

    uid: UUID = Field(default_factory=uuid4)
    documents: Dict[UUID, Document] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
