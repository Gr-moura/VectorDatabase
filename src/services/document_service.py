# src/services/document_service.py

from uuid import UUID
from typing import List
from src.core.models import Document, Chunk, Library
from src.core.indexing.avl_index import AvlIndex
from src.core.indexing.lsh_index import LshIndex
from src.api.schemas import DocumentCreate, DocumentUpdate
from src.infrastructure.repositories.base_repo import ILibraryRepository
from src.infrastructure.embeddings.base_client import IEmbeddingsClient
from src.core.exceptions import DocumentNotFound


class DocumentService:
    def __init__(
        self, repository: ILibraryRepository, embeddings_client: IEmbeddingsClient
    ):
        self.repository = repository
        self.embeddings_client = embeddings_client

    def create_document(self, library_id: UUID, doc_create: DocumentCreate) -> Document:
        library = self.repository.get_by_id(library_id)

        document_data = doc_create.model_dump(exclude={"chunks"})
        document = Document(**document_data)

        # Batch processing of chunk embeddings
        if doc_create.chunks:
            chunks_to_embed: List[Chunk] = []
            texts_to_embed: List[str] = []

            temp_chunks = []
            for chunk_create in doc_create.chunks:
                chunk = Chunk(**chunk_create.model_dump())

                if chunk.text:
                    chunks_to_embed.append(chunk)
                    texts_to_embed.append(chunk.text)

                temp_chunks.append(chunk)

            if texts_to_embed:
                vectors = self.embeddings_client.get_embeddings(texts_to_embed)

                for chunk, vector in zip(chunks_to_embed, vectors):
                    chunk.embedding = vector

            for chunk in temp_chunks:
                document.chunks[chunk.uid] = chunk
                self._update_indices_on_add(library, chunk)

        library.documents[document.uid] = document
        self.repository.update(library)
        return document

    def _update_indices_on_add(self, library: Library, chunk: Chunk):
        if not chunk.embedding:
            return

        for index_name, index in library.indices.items():
            if isinstance(index, (AvlIndex, LshIndex)):
                index.insert(chunk)

                if index_name in library.index_metadata:
                    library.index_metadata[index_name].vector_count = index.vector_count

    def get_document(self, library_id: UUID, doc_id: UUID) -> Document:
        library = self.repository.get_by_id(library_id)
        document = library.documents.get(doc_id)
        if not document:
            raise DocumentNotFound(
                f"Document {doc_id} not found in library {library_id}"
            )
        return document

    def list_documents(self, library_id: UUID) -> List[Document]:
        library = self.repository.get_by_id(library_id)
        return list(library.documents.values())

    def update_document(
        self, library_id: UUID, doc_id: UUID, doc_update: DocumentUpdate
    ) -> Document:
        library = self.repository.get_by_id(library_id)
        document = library.documents.get(doc_id)
        if not document:
            raise DocumentNotFound(
                f"Document {doc_id} not found in library {library_id}"
            )

        update_data = doc_update.model_dump(exclude_unset=True)
        updated_document = document.model_copy(update=update_data)

        library.documents[doc_id] = updated_document
        self.repository.update(library)
        return updated_document

    def delete_document(self, library_id: UUID, doc_id: UUID) -> None:
        library = self.repository.get_by_id(library_id)
        if doc_id not in library.documents:
            raise DocumentNotFound(
                f"Document {doc_id} not found in library {library_id}"
            )

        document = library.documents[doc_id]

        if document.chunks:
            for chunk_id in document.chunks:
                for index in library.indices.values():
                    if isinstance(index, (AvlIndex, LshIndex)):
                        index.delete(chunk_id)

        for index_name, index in library.indices.items():
            if index_name in library.index_metadata:
                library.index_metadata[index_name].vector_count = index.vector_count

        del library.documents[doc_id]
        self.repository.update(library)
