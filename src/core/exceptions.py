# src/core/exceptions.py


class LibraryNotFound(Exception):
    """Raised when a library is not found."""

    pass


class DocumentNotFound(Exception):
    """Raised when a document is not found."""

    pass


class ChunkNotFound(Exception):
    """Raised when a chunk is not found."""

    pass


class IndexNotReady(Exception):
    """Raised when a search is attempted on an un-built index."""

    pass


class IndexNotFound(Exception):
    """Raised when a specified index is not found in the library."""

    pass


class VectorDimensionMismatch(Exception):
    """Raised when there is a dimension mismatch during search operations."""

    pass
