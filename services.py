from schemas import *

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

    def get_library(self, library_uid: UUID) -> Optional[Library]:
        """Get a library by UID."""
        return self.libraries.get(library_uid)

    def update_library(
        self, library_uid: UUID, library_update: LibraryUpdate
    ) -> Optional[Library]:
        """Update a library."""
        library = self.libraries.get(library_uid)
        if not library:
            return None

        update_data = library_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(library, field, value)

        return library

    def delete_library(self, library_uid: UUID) -> bool:
        """Delete a library."""
        if library_uid in self.libraries:
            del self.libraries[library_uid]
            return True
        return False

    def list_libraries(self) -> List[Library]:
        """List all libraries."""
        return list(self.libraries.values())

    # ========================================================================
    # DOCUMENT OPERATIONS
    # ========================================================================

    def create_document(
        self, library_uid: UUID, doc_create: DocumentCreate
    ) -> Optional[Document]:
        """Create a document in a library."""
        library = self.get_library(library_uid)
        if not library:
            return None

        document = Document(**doc_create.model_dump())
        library.documents[document.uid] = document

        # Update index if it exists
        if library.index:
            self._update_index_for_document_add(library, document)

        return document

    def get_document(self, library_uid: UUID, doc_uid: UUID) -> Optional[Document]:
        """Get a document from a library."""
        library = self.get_library(library_uid)
        if library:
            return library.documents.get(doc_uid)
        return None

    def update_document(
        self, library_uid: UUID, doc_uid: UUID, doc_update: DocumentUpdate
    ) -> Optional[Document]:
        """Update a document in a library."""
        library = self.get_library(library_uid)
        if not library or doc_uid not in library.documents:
            return None

        document = library.documents[doc_uid]
        update_data = doc_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(document, field, value)

        # Update index if it exists
        if library.index and "name" in update_data:
            library.index.document_names[doc_uid] = document.name

        return document

    def delete_document(self, library_uid: UUID, doc_uid: UUID) -> bool:
        """Delete a document from a library."""
        library = self.get_library(library_uid)
        if not library or doc_uid not in library.documents:
            return False

        del library.documents[doc_uid]

        # Update index if it exists
        if library.index:
            self._update_index_for_document_delete(library, doc_uid)

        return True

    def list_documents(self, library_uid: UUID) -> Optional[List[Document]]:
        """List all documents in a library."""
        library = self.get_library(library_uid)
        if library:
            return list(library.documents.values())
        return None

    # ========================================================================
    # CHUNK OPERATIONS
    # ========================================================================

    def create_chunk(
        self, library_uid: UUID, doc_uid: UUID, chunk_create: ChunkCreate
    ) -> Optional[Chunk]:
        """Create a chunk in a document."""
        document = self.get_document(library_uid, doc_uid)
        if not document:
            return None

        chunk = Chunk(**chunk_create.model_dump())
        document.chunks[chunk.uid] = chunk

        library = self.get_library(library_uid)
        if library:
            # Update index if it exists
            if library.index:
                self._update_index_for_chunk_add(library, doc_uid, chunk)

        return chunk

    def get_chunk(
        self, library_uid: UUID, doc_uid: UUID, chunk_uid: UUID
    ) -> Optional[Chunk]:
        """Get a chunk from a document."""
        document = self.get_document(library_uid, doc_uid)
        if document:
            return document.chunks.get(chunk_uid)
        return None

    def update_chunk(
        self,
        library_uid: UUID,
        doc_uid: UUID,
        chunk_uid: UUID,
        chunk_update: ChunkUpdate,
    ) -> Optional[Chunk]:
        """Update a chunk in a document."""
        document = self.get_document(library_uid, doc_uid)
        if not document or chunk_uid not in document.chunks:
            return None

        chunk = document.chunks[chunk_uid]
        update_data = chunk_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(chunk, field, value)

        library = self.get_library(library_uid)
        if library:
            # Update index if it exists
            if library.index:
                self._update_index_for_chunk_update(library, doc_uid, chunk)

        return chunk

    def delete_chunk(self, library_uid: UUID, doc_uid: UUID, chunk_uid: UUID) -> bool:
        """Delete a chunk from a document."""
        document = self.get_document(library_uid, doc_uid)
        if not document or chunk_uid not in document.chunks:
            return False

        del document.chunks[chunk_uid]

        library = self.get_library(library_uid)
        if library:
            # Update index if it exists
            if library.index:
                self._update_index_for_chunk_delete(library, doc_uid, chunk_uid)

        return True

    def list_chunks(self, library_uid: UUID, doc_uid: UUID) -> Optional[List[Chunk]]:
        """List all chunks in a document."""
        document = self.get_document(library_uid, doc_uid)
        if document:
            return list(document.chunks.values())
        return None

    # ========================================================================
    # INDEX OPERATIONS
    # ========================================================================

    def build_index(self, library_uid: UUID) -> Optional[LibraryIndex]:
        """Build or rebuild the index for a library."""
        library = self.get_library(library_uid)
        if not library:
            return None

        index = LibraryIndex(
            total_documents=len(library.documents),
            total_chunks=sum(len(doc.chunks) for doc in library.documents.values()),
        )

        for doc_uid, document in library.documents.items():
            index.document_names[doc_uid] = document.name
            index.chunk_texts[doc_uid] = {}
            index.embeddings[doc_uid] = {}

            for chunk_uid, chunk in document.chunks.items():
                index.chunk_texts[doc_uid][chunk_uid] = chunk.text
                if chunk.embedding:
                    index.embeddings[doc_uid][chunk_uid] = chunk.embedding

        library.index = index
        return index

    # ========================================================================
    # PRIVATE INDEX UPDATE HELPERS
    # ========================================================================

    def _update_index_for_document_add(self, library: Library, document: Document):
        """Update index when a document is added."""
        if not library.index:
            return

        library.index.total_documents += 1
        library.index.document_names[document.uid] = document.name
        library.index.chunk_texts[document.uid] = {}
        library.index.embeddings[document.uid] = {}

    def _update_index_for_document_delete(self, library: Library, doc_uid: UUID):
        """Update index when a document is deleted."""
        if not library.index:
            return

        library.index.total_documents -= 1
        if doc_uid in library.index.document_names:
            del library.index.document_names[doc_uid]
        if doc_uid in library.index.chunk_texts:
            library.index.total_chunks -= len(library.index.chunk_texts[doc_uid])
            del library.index.chunk_texts[doc_uid]
        if doc_uid in library.index.embeddings:
            del library.index.embeddings[doc_uid]

    def _update_index_for_chunk_add(
        self, library: Library, doc_uid: UUID, chunk: Chunk
    ):
        """Update index when a chunk is added."""
        if not library.index:
            return

        library.index.total_chunks += 1
        if doc_uid not in library.index.chunk_texts:
            library.index.chunk_texts[doc_uid] = {}
            library.index.embeddings[doc_uid] = {}

        library.index.chunk_texts[doc_uid][chunk.uid] = chunk.text
        if chunk.embedding:
            library.index.embeddings[doc_uid][chunk.uid] = chunk.embedding

    def _update_index_for_chunk_update(
        self, library: Library, doc_uid: UUID, chunk: Chunk
    ):
        """Update index when a chunk is updated."""
        if not library.index:
            return

        if doc_uid in library.index.chunk_texts:
            library.index.chunk_texts[doc_uid][chunk.uid] = chunk.text
            if chunk.embedding:
                library.index.embeddings[doc_uid][chunk.uid] = chunk.embedding
            elif chunk.uid in library.index.embeddings.get(doc_uid, {}):
                del library.index.embeddings[doc_uid][chunk.uid]

    def _update_index_for_chunk_delete(
        self, library: Library, doc_uid: UUID, chunk_uid: UUID
    ):
        """Update index when a chunk is deleted."""
        if not library.index:
            return

        library.index.total_chunks -= 1
        if (
            doc_uid in library.index.chunk_texts
            and chunk_uid in library.index.chunk_texts[doc_uid]
        ):
            del library.index.chunk_texts[doc_uid][chunk_uid]
        if (
            doc_uid in library.index.embeddings
            and chunk_uid in library.index.embeddings[doc_uid]
        ):
            del library.index.embeddings[doc_uid][chunk_uid]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize service (this would be your API layer)
    service = LibraryService()

    # Create a library
    library = service.create_library(
        LibraryCreate(name="My Library", metadata={"owner": "admin"})
    )
    print(f"Created library: {library.uid}")

    # Create a document
    doc = service.create_document(
        library.uid, DocumentCreate(name="Document 1", metadata={"category": "science"})
    )
    print(f"Created document: {doc.uid}")

    # Create chunks
    chunk1 = service.create_chunk(
        library.uid,
        doc.uid,
        ChunkCreate(text="First chunk of text", embedding=[0.1, 0.2, 0.3]),
    )
    chunk2 = service.create_chunk(
        library.uid,
        doc.uid,
        ChunkCreate(text="Second chunk of text", embedding=[0.4, 0.5, 0.6]),
    )

    print(f"Created chunks: {chunk1.uid}, {chunk2.uid}")

    # Build index
    index = service.build_index(library.uid)
    print(
        f"Built index: {index.total_documents} documents, {index.total_chunks} chunks"
    )

    # Update a chunk (index is automatically updated)
    updated_chunk = service.update_chunk(
        library.uid, doc.uid, chunk1.uid, ChunkUpdate(text="Updated chunk text")
    )
    print(f"Updated chunk: {updated_chunk.text}")

    # Delete a chunk (index is automatically updated)
    success = service.delete_chunk(library.uid, doc.uid, chunk2.uid)
    print(f"Deleted chunk: {success}")

    # Check updated index
    updated_library = service.get_library(library.uid)
    print(f"Final index: {updated_library.index.total_chunks} chunks")
