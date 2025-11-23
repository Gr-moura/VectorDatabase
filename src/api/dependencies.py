# vector_db_project/src/api/dependencies.py

from fastapi.params import Depends
from src.infrastructure.repositories.base_repo import ILibraryRepository
from src.infrastructure.repositories.in_memory_repo import InMemoryLibraryRepository
from src.services.library_service import LibraryService
from src.services.document_service import DocumentService
from src.services.chunk_service import ChunkService
from src.services.search_service import SearchService
from src.infrastructure.embeddings.base_client import IEmbeddingsClient
from src.infrastructure.embeddings.cohere_client import CohereClient


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

# Create a single repository instance to be shared across the application lifecycle.
# This acts as our in-memory "database". Its state is shared across all requests.
# The type hint ensures we can easily swap it for another implementation later.
library_repository: ILibraryRepository = InMemoryLibraryRepository()


# ============================================================================
# DEPENDENCY PROVIDERS (GETTERS)
# ============================================================================

# Each of these functions is a "dependency" that FastAPI can inject into
# your API endpoint functions.


def get_embeddings_client() -> IEmbeddingsClient:
    """Provides a real Cohere embeddings client for the application."""
    return CohereClient()


def get_library_service() -> LibraryService:
    """Provides a LibraryService instance initialized with our singleton repository."""
    return LibraryService(repository=library_repository)


def get_document_service(
    embeddings_client: IEmbeddingsClient = Depends(get_embeddings_client),
) -> DocumentService:
    """Provides a DocumentService instance."""
    return DocumentService(
        repository=library_repository, embeddings_client=embeddings_client
    )


def get_chunk_service() -> ChunkService:
    """Provides a ChunkService instance initialized with our singleton repository."""
    return ChunkService(repository=library_repository)


def get_search_service() -> SearchService:
    """
    Provides a SearchService instance.
    Since SearchService is now stateless (it operates on the index stored within
    the Library object), we can create a new instance for each request without issue.
    """
    return SearchService(repository=library_repository)


def get_chunk_service(
    embeddings_client: IEmbeddingsClient = Depends(get_embeddings_client),
) -> ChunkService:
    """Provides a ChunkService with necessary dependencies."""
    return ChunkService(
        repository=library_repository, embeddings_client=embeddings_client
    )
