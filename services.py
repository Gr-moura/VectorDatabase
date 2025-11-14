from uuid import UUID
from typing import Dict, List

from schemas import (
    Library,
    LibraryCreate,
    LibraryUpdate,
    Document,
    DocumentCreate,
    DocumentUpdate,
    Chunk,
    ChunkCreate,
    ChunkUpdate,
)
from exceptions import LibraryNotFound, DocumentNotFound, ChunkNotFound

# ============================================================================
# SERVICE LAYER (API LOGIC)
# ============================================================================


class LibraryService:
    """
    Service layer that handles all CRUD operations.
    """

    def __init__(self):
        self.libraries: Dict[UUID, Library] = {}

    # ========================================================================
    # LIBRARY OPERATIONS
    # ========================================================================

    def create_library(self, library_create: LibraryCreate) -> Library:
        """Create a new library."""
        library = Library(**library_create.model_dump())
        self.libraries[library.uid] = library
        return library

    def get_library(self, library_uid: UUID) -> Library:
        """Get a library by UID."""
        library = self.libraries.get(library_uid)
        if library:
            return library

        raise LibraryNotFound(f"Library with id {library_uid} not found")

    def update_library(
        self, library_uid: UUID, library_update: LibraryUpdate
    ) -> Library:
        """Update a library."""
        library = self.get_library(library_uid)

        update_data = library_update.model_dump(exclude_unset=True)
        library = library.model_copy(update=update_data)
        self.libraries[library_uid] = library

        return library

    def delete_library(self, library_uid: UUID) -> None:
        """Delete a library."""
        if library_uid in self.libraries:
            del self.libraries[library_uid]
            return

        raise LibraryNotFound(f"Library with id {library_uid} not found")

    def list_libraries(self) -> List[Library]:
        """List all libraries."""
        return list(self.libraries.values())

    # ========================================================================
    # DOCUMENT OPERATIONS
    # ========================================================================

    def create_document(
        self, library_uid: UUID, doc_create: DocumentCreate
    ) -> Document:
        """Create a document in a library."""
        library = self.get_library(library_uid)

        document = Document(**doc_create.model_dump())
        library.documents[document.uid] = document

        return document

    def get_document(self, library_uid: UUID, doc_uid: UUID) -> Document:
        """Get a document from a library."""
        library = self.get_library(library_uid)

        document = library.documents.get(doc_uid)
        if document:
            return document

        raise DocumentNotFound(
            f"Document with id {doc_uid} not found in library {library_uid}"
        )

    def update_document(
        self, library_uid: UUID, doc_uid: UUID, doc_update: DocumentUpdate
    ) -> Document:
        """Update a document in a library."""
        document = self.get_document(library_uid, doc_uid)

        update_data = doc_update.model_dump(exclude_unset=True)
        document = document.model_copy(update=update_data)

        library = self.get_library(library_uid)
        library.documents[doc_uid] = document

        return document

    def delete_document(self, library_uid: UUID, doc_uid: UUID) -> None:
        """Delete a document from a library."""
        library = self.get_library(library_uid)

        if doc_uid in library.documents:
            del library.documents[doc_uid]
            return

        raise DocumentNotFound(
            f"Document with id {doc_uid} not found in library {library_uid}"
        )

    def list_documents(self, library_uid: UUID) -> List[Document]:
        """List all documents in a library."""
        library = self.get_library(library_uid)
        return list(library.documents.values())

    # ========================================================================
    # CHUNK OPERATIONS
    # ========================================================================

    def create_chunk(
        self, library_uid: UUID, doc_uid: UUID, chunk_create: ChunkCreate
    ) -> Chunk:
        """Create a chunk in a document."""
        document = self.get_document(library_uid, doc_uid)

        chunk = Chunk(**chunk_create.model_dump())
        document.chunks[chunk.uid] = chunk

        return chunk

    def get_chunk(self, library_uid: UUID, doc_uid: UUID, chunk_uid: UUID) -> Chunk:
        """Get a chunk from a document."""
        document = self.get_document(library_uid, doc_uid)

        chunk = document.chunks.get(chunk_uid)
        if chunk:
            return chunk

        raise ChunkNotFound(
            f"Chunk with id {chunk_uid} not found in document {doc_uid}"
        )

    def update_chunk(
        self,
        library_uid: UUID,
        doc_uid: UUID,
        chunk_uid: UUID,
        chunk_update: ChunkUpdate,
    ) -> Chunk:
        """Update a chunk in a document."""
        chunk = self.get_chunk(library_uid, doc_uid, chunk_uid)

        update_data = chunk_update.model_dump(exclude_unset=True)
        chunk = chunk.model_copy(update=update_data)

        document = self.get_document(library_uid, doc_uid)
        document.chunks[chunk_uid] = chunk

        return chunk

    def delete_chunk(self, library_uid: UUID, doc_uid: UUID, chunk_uid: UUID) -> None:
        """Delete a chunk from a document."""
        document = self.get_document(library_uid, doc_uid)

        if chunk_uid in document.chunks:
            del document.chunks[chunk_uid]
            return

        raise ChunkNotFound(
            f"Chunk with id {chunk_uid} not found in document {doc_uid}"
        )

    def list_chunks(self, library_uid: UUID, doc_uid: UUID) -> List[Chunk]:
        """List all chunks in a document."""
        document = self.get_document(library_uid, doc_uid)
        return list(document.chunks.values())
