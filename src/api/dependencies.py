# src/api/dependencies.py

from functools import lru_cache
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

library_repository: ILibraryRepository = InMemoryLibraryRepository()

# ============================================================================
# DEPENDENCY PROVIDERS
# ============================================================================


@lru_cache()
def get_embeddings_client() -> IEmbeddingsClient:
    """
    Provides a singleton Cohere embeddings client.
    LRU Cache ensures we reuse the connection pool across requests.
    """
    return CohereClient()


def get_library_service() -> LibraryService:
    return LibraryService(repository=library_repository)


def get_document_service(
    embeddings_client: IEmbeddingsClient = Depends(get_embeddings_client),
) -> DocumentService:
    return DocumentService(
        repository=library_repository, embeddings_client=embeddings_client
    )


def get_chunk_service(
    embeddings_client: IEmbeddingsClient = Depends(get_embeddings_client),
) -> ChunkService:
    """Provides a ChunkService with necessary dependencies."""
    return ChunkService(
        repository=library_repository, embeddings_client=embeddings_client
    )


def get_search_service(
    embeddings_client: IEmbeddingsClient = Depends(get_embeddings_client),
) -> SearchService:
    return SearchService(
        repository=library_repository, embeddings_client=embeddings_client
    )
