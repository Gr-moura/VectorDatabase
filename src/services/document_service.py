# vector_db_project/src/services/document_service.py

from uuid import UUID
from typing import List
from src.core.models import Document, Chunk
from src.api.schemas import DocumentCreate, DocumentUpdate
from src.infrastructure.repositories.base_repo import ILibraryRepository
from src.core.exceptions import DocumentNotFound


class DocumentService:
    def __init__(self, repository: ILibraryRepository):
        self.repository = repository

    def create_document(self, library_id: UUID, doc_create: DocumentCreate) -> Document:
        library = self.repository.get_by_id(library_id)

        document_data = doc_create.model_dump(exclude={"chunks"})
        document = Document(**document_data)

        if doc_create.chunks:
            for chunk_create in doc_create.chunks:
                chunk = Chunk(**chunk_create.model_dump())
                document.chunks[chunk.uid] = chunk

        library.documents[document.uid] = document
        self.repository.update(library)
        return document

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

        del library.documents[doc_id]
        self.repository.update(library)
