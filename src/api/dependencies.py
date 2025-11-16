# vector_db_project/src/api/dependencies.py

from src.infrastructure.repositories.in_memory_repo import InMemoryLibraryRepository
from src.services.library_service import LibraryService
from src.services.document_service import DocumentService
from src.services.chunk_service import ChunkService
from src.services.search_service import SearchService
from src.core.indexing.flat_index import FlatIndex

# Create a single repository instance to be shared across the application lifecycle.
# This simulates a database connection pool.
library_repository = InMemoryLibraryRepository()

# Create a single index instance for the same reason.
# In a real app, you might have a factory that creates indexes per library.
vector_index = FlatIndex()


def get_library_service() -> LibraryService:
    return LibraryService(repository=library_repository)


def get_document_service() -> DocumentService:
    return DocumentService(repository=library_repository)


def get_chunk_service() -> ChunkService:
    return ChunkService(repository=library_repository)


def get_search_service() -> SearchService:
    return SearchService(repository=library_repository, index=vector_index)
