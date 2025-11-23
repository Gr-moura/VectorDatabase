# vector_db_project/src/services/chunk_service.py

from uuid import UUID
from typing import List
from src.core.models import Library, Chunk
from src.api.schemas import ChunkCreate, ChunkUpdate
from src.infrastructure.repositories.base_repo import ILibraryRepository
from src.core.exceptions import DocumentNotFound
from src.core.exceptions import ChunkNotFound
from src.core.indexing.avl_index import AvlIndex
from src.infrastructure.embeddings.base_client import IEmbeddingsClient


class ChunkService:
    def __init__(
        self, repository: ILibraryRepository, embeddings_client: IEmbeddingsClient
    ):
        self.repository = repository
        self.embeddings_client = embeddings_client

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

    def _update_indices_on_add_update(self, library: Library, chunk: Chunk):
        """Updates all indices of a library after a chunk addition/update."""
        for index_name, index in library.indices.items():
            if isinstance(index, AvlIndex):
                index.insert(chunk)

                # Also update the corresponding metadata object.
                if index_name in library.index_metadata:
                    library.index_metadata[index_name].vector_count = index.vector_count

                print(f"AvlIndex '{index_name}' updated for chunk {chunk.uid}.")
            else:
                pass  # Handle other index types as needed

    def _update_indices_on_delete(self, library: Library, chunk_id: UUID):
        """Updates all indices of a library after a chunk deletion."""
        for index_name, index in list(library.indices.items()):
            if isinstance(index, AvlIndex):
                index.delete(chunk_id)

                # Also update the corresponding metadata object.
                if index_name in library.index_metadata:
                    library.index_metadata[index_name].vector_count = index.vector_count

                print(f"Chunk {chunk_id} deleted from AvlIndex '{index_name}'.")
            else:
                pass  # Handle other index types as needed

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
        if chunk.text:
            chunk.embedding = self.embeddings_client.get_embeddings([chunk.text])[0]

        document.chunks[chunk.uid] = chunk

        self._update_indices_on_add_update(library, chunk)

        self.repository.update(library)

        return chunk

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

        if chunk_update.text is not None:
            new_embedding = self.embeddings_client.get_embeddings([chunk_update.text])[
                0
            ]
            update_data["embedding"] = new_embedding

        updated_chunk = chunk.model_copy(update=update_data)
        document.chunks[chunk_id] = updated_chunk

        # Update indices only if text was changed (and thus embedding)
        if chunk_update.text is not None:
            self._update_indices_on_add_update(library, updated_chunk)

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

        self._update_indices_on_delete(library, chunk_id)
        self.repository.update(library)
