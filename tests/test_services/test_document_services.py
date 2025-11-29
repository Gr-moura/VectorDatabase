# tests/test_services/test_document_services.py

import unittest
from uuid import uuid4
from typing import List

from src.core.models import Library
from src.core.indexing.avl_index import AvlIndex
from src.core.indexing.lsh_index import LshIndex
from src.infrastructure.repositories.in_memory_repo import InMemoryLibraryRepository
from src.services.document_service import DocumentService
from src.api.schemas import DocumentCreate, ChunkCreate

# --- Mock Infrastructure ---


class MockEmbeddingsClient:
    """Deterministic mock to avoid network/API calls."""

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Returns fixed vectors based on text length just to populate the field
        return [[0.1, 0.2] for _ in texts]


# --- Integration Tests ---


class TestDocumentServiceFixes(unittest.TestCase):

    def setUp(self):
        self.repo = InMemoryLibraryRepository()
        self.embeddings_client = MockEmbeddingsClient()
        self.service = DocumentService(self.repo, self.embeddings_client)

        # Setup: Create a library with BOTH index types
        self.lib_id = uuid4()
        self.library = Library(uid=self.lib_id, name="Test Lib")

        # AVL Index (Already worked, but testing regression)
        self.library.indices["avl_main"] = AvlIndex()
        # LSH Index (Where the silencing bug existed)
        self.library.indices["lsh_main"] = LshIndex(num_bits=4, num_tables=2)

        self.repo.add(self.library)

    def test_create_document_populates_lsh_index(self):
        """
        Reproduces Bug #2: The old code ignored 'isinstance(index, LshIndex)'.
        This test will fail if the LSH is not updated.
        """
        doc_create = DocumentCreate(
            name="LSH Test Doc", chunks=[ChunkCreate(text="Hello LSH", uid=uuid4())]
        )

        # Action
        self.service.create_document(self.lib_id, doc_create)

        # Refresh state
        updated_lib = self.repo.get_by_id(self.lib_id)
        lsh_index = updated_lib.indices["lsh_main"]

        # Assert
        self.assertEqual(
            lsh_index.vector_count,
            1,
            "Critical Failure: LSHIndex was ignored during document creation.",
        )

    def test_delete_document_removes_vectors_from_indices(self):
        """
        Reproduces Bug #1 (Ghost Data): Deleting the document kept vectors in the index.
        """
        # 1. Setup Data
        chunk_id = uuid4()
        doc_create = DocumentCreate(
            name="Ghost Doc",
            chunks=[ChunkCreate(text="I will be deleted", uid=chunk_id)],
        )
        doc = self.service.create_document(self.lib_id, doc_create)
        doc_id = doc.uid

        # Verify insertion
        lib_before = self.repo.get_by_id(self.lib_id)
        self.assertEqual(lib_before.indices["avl_main"].vector_count, 1)

        # 2. Action: Delete Document
        self.service.delete_document(self.lib_id, doc_id)

        # 3. Assert Indices are Clean
        lib_after = self.repo.get_by_id(self.lib_id)

        avl_count = lib_after.indices["avl_main"].vector_count
        lsh_count = lib_after.indices["lsh_main"].vector_count

        self.assertEqual(
            avl_count,
            0,
            f"Ghost Data detected in AVL! Expected 0, found {avl_count}",
        )
        self.assertEqual(
            lsh_count,
            0,
            f"Ghost Data detected in LSH! Expected 0, found {lsh_count}",
        )

    def test_search_consistency_after_delete(self):
        """
        Simulates runtime crash: Search returns an ID that no longer exists in Documents.
        """
        # 1. Create
        chunk_id = uuid4()
        doc_create = DocumentCreate(
            name="Zombie Doc", chunks=[ChunkCreate(text="Search me", uid=chunk_id)]
        )
        self.service.create_document(self.lib_id, doc_create)

        # 2. Delete
        doc = self.service.list_documents(self.lib_id)[0]
        self.service.delete_document(self.lib_id, doc.uid)

        # 3. Search directly on the index (simulating a query)
        # If the bug persists, the index will return the deleted chunk_id.
        lib = self.repo.get_by_id(self.lib_id)
        avl_index = lib.indices["avl_main"]

        # Dummy query vector
        results = avl_index.search([0.1, 0.2], k=1)

        # Assert
        # If cleanup worked, results should be empty.
        self.assertEqual(
            len(results),
            0,
            "Inconsistency: Search returned a chunk from a deleted document.",
        )
