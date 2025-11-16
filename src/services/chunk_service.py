# vector_db_project/src/services/chunk_service.py

from uuid import UUID
from typing import List
from src.core.models import Chunk
from src.api.schemas import ChunkCreate, ChunkUpdate
from src.infrastructure.repositories.base_repo import ILibraryRepository
from src.core.exceptions import DocumentNotFound
from src.core.exceptions import ChunkNotFound


class ChunkService:
    def __init__(self, repository: ILibraryRepository):
        self.repository = repository

    def create_chunk(
        self, library_id: UUID, doc_id: UUID, chunk_create: ChunkCreate
    ) -> Chunk:
        library = self.repository.get_by_id(library_id)
        document = library.documents.get(doc_id)
        if not document:
            # This check is now implicit, but good to be aware of
            raise DocumentNotFound(
                f"Document {doc_id} not found in library {library_id}"
            )

        chunk = Chunk(**chunk_create.model_dump())
        document.chunks[chunk.uid] = chunk

        self.repository.update(library)

        return chunk

    def get_chunk(self, library_id: UUID, doc_id: UUID, chunk_id: UUID) -> Chunk:
        library = self.repository.get_by_id(library_id)
        document = library.documents.get(doc_id)
        if not document:
            raise DocumentNotFound(
                f"Document {doc_id} not found in library {library_id}"
            )

        chunk = document.chunks.get(chunk_id)
        if not chunk:
            raise ChunkNotFound(f"Chunk {chunk_id} not found in document {doc_id}")
        return chunk

    def list_chunks(self, library_id: UUID, doc_id: UUID) -> List[Chunk]:
        library = self.repository.get_by_id(library_id)
        document = library.documents.get(doc_id)
        if not document:
            raise DocumentNotFound(
                f"Document {doc_id} not found in library {library_id}"
            )
        return list(document.chunks.values())

    def update_chunk(
        self, library_id: UUID, doc_id: UUID, chunk_id: UUID, chunk_update: ChunkUpdate
    ) -> Chunk:
        library = self.repository.get_by_id(library_id)
        document = library.documents.get(doc_id)
        if not document:
            raise DocumentNotFound(
                f"Document {doc_id} not found in library {library_id}"
            )

        chunk = document.chunks.get(chunk_id)
        if not chunk:
            raise ChunkNotFound(f"Chunk {chunk_id} not found in document {doc_id}")

        update_data = chunk_update.model_dump(exclude_unset=True)
        updated_chunk = chunk.model_copy(update=update_data)

        document.chunks[chunk_id] = updated_chunk

        self.repository.update(library)

        return updated_chunk

    def delete_chunk(self, library_id: UUID, doc_id: UUID, chunk_id: UUID) -> None:
        library = self.repository.get_by_id(library_id)
        document = library.documents.get(doc_id)
        if not document:
            raise DocumentNotFound(
                f"Document {doc_id} not found in library {library_id}"
            )

        if chunk_id not in document.chunks:
            raise ChunkNotFound(f"Chunk {chunk_id} not found in document {doc_id}")

        del document.chunks[chunk_id]

        self.repository.update(library)
