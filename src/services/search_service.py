# vector_db_project/src/services/search_service.py

from uuid import UUID
from typing import List
from src.api.schemas import SearchResult
from src.infrastructure.repositories.base_repo import ILibraryRepository
from src.core.indexing.base_index import VectorIndex
from src.core.models import Chunk


class SearchService:
    def __init__(self, repository: ILibraryRepository, index: VectorIndex):
        self.repository = repository
        self.index = index

    def search_chunks(
        self, library_id: UUID, query_embedding: List[float], k: int
    ) -> List[SearchResult]:
        library = self.repository.get_by_id(library_id)

        # 1. Collect all chunks and their embeddings from the library
        all_chunks: List[Chunk] = []
        for document in library.documents.values():
            for chunk in document.chunks.values():
                if chunk.embedding:
                    all_chunks.append(chunk)

        if not all_chunks:
            return []

        # 2. Add vectors to the index (in a real app, this would be pre-built)
        # For simplicity here, we build it on the fly for each query.
        self.index.build(all_chunks)

        # 3. Perform the search using the injected index implementation
        search_results = self.index.search(query_embedding, k)

        # 4. Format the results into the API schema
        return [
            SearchResult(chunk=chunk, similarity=score)
            for chunk, score in search_results
        ]
