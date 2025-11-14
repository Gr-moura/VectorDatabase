# src/api/dependencies.py

"""
FastAPI dependency injection setup.

This module is responsible for instantiating and wiring up the application's
dependencies, such as services and repositories. It allows the API layer
to remain decoupled from the business logic and data access implementations.
"""

# Note: The following imports are placeholders for the actual implementations
# that would exist in the other layers of the application.

# from src.infrastructure.repositories.in_memory_repo import (
#     in_memory_library_repository,
#     in_memory_chunk_repository,
# )
# from src.services.library_service import LibraryService
# from src.services.chunk_service import ChunkService
# from src.services.search_service import SearchService
# from src.core.indexing.factory import IndexFactory

# --- Mock Implementations for demonstration ---
# In a real application, these would be the actual imported classes.


class MockRepo:
    """A mock repository to stand in for a real implementation."""

    def __init__(self, name: str):
        self._name = name
        print(f"Instantiated MockRepo: {self._name}")


class MockService:
    """A mock service to stand in for a real implementation."""

    def __init__(self, *args, **kwargs):
        pass


# Instantiate singleton repositories
# This pattern ensures all services use the same in-memory data store.
library_repository = MockRepo("LibraryRepository")
chunk_repository = MockRepo("ChunkRepository")

# --- Dependency Provider Functions ---


def get_library_service() -> MockService:
    """
    Dependency provider for the LibraryService.

    Initializes the service with its required repository. FastAPI will cache
    the result for the scope of a single request.
    """
    # In a real app:
    # return LibraryService(repository=library_repository)
    return MockService(repository=library_repository)


def get_chunk_service() -> MockService:
    """Dependency provider for the ChunkService."""
    # In a real app:
    # return ChunkService(
    #     chunk_repository=chunk_repository,
    #     library_repository=library_repository
    # )
    return MockService(
        chunk_repository=chunk_repository, library_repository=library_repository
    )


def get_search_service() -> MockService:
    """Dependency provider for the SearchService."""
    # In a real app:
    # index_factory = IndexFactory()
    # return SearchService(
    #     library_repository=library_repository,
    #     index_factory=index_factory
    # )
    return MockService(library_repository=library_repository)
