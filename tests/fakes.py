# tests/fakes.py

from uuid import uuid4
from typing import Dict, Any, List, Optional

# ============================================================================
# Fake Domain Model Classes for Unit Testing
# ============================================================================


class FakeChunk:
    """A fake version of the core.models.Chunk for unit tests."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.uid = getattr(self, "uid", uuid4())
        self.embedding = getattr(self, "embedding", None)
        self.text = getattr(self, "text", "")
        self.metadata = getattr(self, "metadata", {})

    def model_copy(self, update: Optional[Dict[str, Any]] = None) -> "FakeChunk":
        data = self.__dict__.copy()
        if update:
            data.update(update)
        return FakeChunk(**data)

    def model_dump(self, exclude=None, exclude_unset=False) -> Dict[str, Any]:
        """Simulates Pydantic model_dump by returning instance attributes."""
        return self.__dict__.copy()


class FakeChunkResponse:
    """A logic-less fake for api.schemas.ChunkResponse."""

    def __init__(self, id, document_id, library_id, text, embedding, metadata):
        self.id = id
        self.document_id = document_id
        self.library_id = library_id
        self.text = text
        self.embedding = embedding
        self.metadata = metadata

    @classmethod
    def from_model(cls, chunk, library_id, document_id):
        return cls(
            id=chunk.uid,
            document_id=document_id,
            library_id=library_id,
            text=chunk.text,
            embedding=chunk.embedding,
            metadata=chunk.metadata,
        )


class FakeDocument:
    """A fake version of the core.models.Document for unit tests."""

    def __init__(self, uid=None, chunks=None, **kwargs):
        self.uid = uid or uuid4()
        self.chunks = chunks if chunks is not None else {}
        self.metadata = kwargs.get("metadata", {})
        # Set any other passed attributes
        for k, v in kwargs.items():
            if not hasattr(self, k):
                setattr(self, k, v)

    def model_copy(self, update: Optional[Dict[str, Any]] = None) -> "FakeDocument":
        data = self.__dict__.copy()
        if update:
            data.update(update)
        # Ensure chunks is a new dict to prevent side effects
        new_doc = FakeDocument(**data)
        new_doc.chunks = dict(self.chunks)
        return new_doc

    def model_dump(self, exclude=None, exclude_unset=False) -> Dict[str, Any]:
        """Simulates Pydantic model_dump by returning instance attributes."""
        return self.__dict__.copy()


class FakeLibrary:
    """A fake version of the core.models.Library for unit tests."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        # Ensure that all attributes expected by services always exist
        self.uid = getattr(self, "uid", uuid4())
        self.documents = getattr(self, "documents", {})
        self.indices = getattr(self, "indices", {})
        self.index_metadata = getattr(self, "index_metadata", {})
        self.metadata = getattr(self, "metadata", {})

    def model_copy(self, update: Optional[Dict[str, Any]] = None) -> "FakeLibrary":
        data = self.__dict__.copy()
        if update:
            data.update(update)
        # Ensure nested dicts are copied to prevent test contamination
        new_lib = FakeLibrary(**data)
        new_lib.documents = dict(self.documents)
        new_lib.indices = dict(self.indices)
        new_lib.index_metadata = dict(self.index_metadata)
        return new_lib

    def model_dump(self, exclude=None, exclude_unset=False) -> Dict[str, Any]:
        """Simulates Pydantic model_dump by returning instance attributes."""
        return self.__dict__.copy()


# ============================================================================
# Fake API Schema Classes for Unit Testing
# ============================================================================


class FakeSchema:
    """A minimal fake for api.schemas objects that provides model_dump()."""

    def __init__(self, data: Dict[str, Any]):
        self._data = dict(data)
        # Initialize chunks specifically if present
        self.chunks: Optional[List["FakeSchema"]] = self._data.get("chunks")

    def __getattr__(self, name):
        """
        Dynamically return attributes from the internal data dict.
        This allows schema.text, schema.uid, etc. to work.
        """
        if name in self._data:
            return self._data[name]
        return None

    def model_dump(
        self, exclude_unset: bool = False, exclude: Optional[set] = None
    ) -> Dict[str, Any]:
        """Mimics Pydantic's model_dump behavior used in services."""
        if exclude_unset:
            # Simple simulation: return everything because 'unset' logic is complex in fakes
            return dict(self._data)
        if exclude:
            return {k: v for k, v in self._data.items() if k not in exclude}
        return dict(self._data)


# ============================================================================
# Fakes for Pydantic Models & Domain Objects
# ============================================================================


class FakeSearchResult:
    """A logic-less fake for api.schemas.SearchResult."""

    def __init__(self, chunk, similarity):
        self.chunk = chunk
        self.similarity = similarity


class FakeIndexMetadata:
    """A logic-less fake for core.models.IndexMetadata."""

    def __init__(self, name, config, vector_count, index_type):
        self.name = name
        self.config = config
        self.vector_count = vector_count
        self.index_type = index_type

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
