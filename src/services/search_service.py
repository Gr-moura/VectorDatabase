# src/services/search_service.py

from uuid import UUID
from typing import List, Dict
from src.api.schemas import SearchResult, IndexCreate
from src.infrastructure.repositories.base_repo import ILibraryRepository
from src.core.indexing.index_factory import IndexFactory, IndexType
from src.core.models import Chunk, Library, IndexMetadata, IndexConfig
from src.core.exceptions import IndexNotReady


class SearchService:
    def __init__(self, repository: ILibraryRepository):
        self.repository = repository

    def create_index(self, library_id: UUID, index_name: str, api_config: IndexCreate):
        """Creates an index and attaches it to the Library object in the repository."""
        library = self.repository.get_by_id(library_id)

        all_chunks: List[Chunk] = [
            chunk
            for document in library.documents.values()
            for chunk in document.chunks.values()
            if chunk.embedding
        ]

        # 1. Create the core IndexConfig object from the API's IndexCreate object.
        core_config = IndexConfig(
            index_type=api_config.index_type,
            metric=api_config.metric,
        )

        # 2. Use the properties from the core_config to create the index.
        index = IndexFactory.create_index(
            index_type=core_config.index_type,
            metric=core_config.metric,
        )

        index.build(all_chunks)

        metadata = IndexMetadata(
            name=index_name,
            config=core_config,
            vector_count=len(all_chunks),
            index_type=core_config.index_type.value,
        )

        # Attach the newly built index directly to the library object
        library.indices[index_name] = index
        library.index_metadata[index_name] = metadata

        # Save the library with its new index back to the repository
        self.repository.update(library)
        print(
            f"Index of type '{core_config.index_type.value}' attached to library {library_id}."
        )

    def get_index_status(self, library_id: UUID, index_name: str) -> dict:
        """Checks the status of a specific named index."""
        library = self.repository.get_by_id(library_id)
        metadata = library.index_metadata.get(index_name)
        if not metadata:
            raise IndexNotReady(
                f"Index with name '{index_name}' not found in library {library_id}."
            )
        return metadata

    def list_all_indices(self, library_id: UUID) -> Dict[str, IndexMetadata]:
        """Lists all indices and their metadata for a given library."""
        library = self.repository.get_by_id(library_id)
        return library.index_metadata

    def delete_index(self, library_id: UUID, index_name: str):
        """Deletes a named index from a library."""
        library = self.repository.get_by_id(library_id)

        if index_name not in library.index_metadata:
            raise IndexNotReady(
                f"Index with name '{index_name}' not found in library {library_id}."
            )

        library.indices.pop(index_name, None)
        library.index_metadata.pop(index_name, None)
        self.repository.update(library)

    def search_chunks(
        self, library_id: UUID, index_name: str, query_embedding: List[float], k: int
    ) -> List[SearchResult]:
        """Performs a search using the index attached to the library."""
        library = self.repository.get_by_id(library_id)
        index = library.indices.get(index_name)

        if not index:
            raise IndexNotReady(
                f"Index '{index_name}' is not ready for search. It may need to be rebuilt."
            )

        search_results = index.search(query_embedding, k)
        return [
            SearchResult(chunk=chunk, similarity=score)
            for chunk, score in search_results
        ]
