# vector_db_project/src/core/indexing/flat_index.py

from typing import List, Tuple
import numpy as np
from src.core.models import Chunk
from .base_index import VectorIndex
from src.core.exceptions import IndexNotReady


class FlatIndex(VectorIndex):
    """A simple brute-force (flat) vector index using L2 distance or cosine similarity."""

    def __init__(self):
        self._matrix: np.ndarray | None = None
        self._chunks: List[Chunk] = []

    def build(self, chunks: List[Chunk]):
        """Builds the index from a list of chunks."""
        if not chunks:
            self._matrix = None
            self._chunks = []
            return

        embeddings = [
            chunk.embedding for chunk in chunks if chunk.embedding is not None
        ]
        if not embeddings:
            self._matrix = None
            self._chunks = []
            return

        self._matrix = np.array(embeddings, dtype=np.float32)
        self._chunks = chunks

    def search(self, query_embedding: List[float], k: int) -> List[Tuple[Chunk, float]]:
        if self._matrix is None or not self._chunks:
            raise IndexNotReady("The index is not built or is empty.")

        query_vector = np.array(query_embedding, dtype=np.float32)

        # Normalize vectors for cosine similarity calculation: A.B / (|A|*|B|)
        query_norm = np.linalg.norm(query_vector)
        matrix_norms = np.linalg.norm(self._matrix, axis=1)

        # Avoid division by zero
        if query_norm == 0 or np.any(matrix_norms == 0):
            return []

        # Calculate cosine similarity
        similarities = np.dot(self._matrix, query_vector) / (matrix_norms * query_norm)

        # Get the top k indices
        # `np.argsort` returns indices that would sort the array in ascending order.
        # We take the last k indices `[-k:]` and reverse them `[::-1]` for descending order.
        num_results = min(k, len(similarities))
        top_k_indices = np.argsort(similarities)[-num_results:][::-1]

        # Format and return the results
        results = [(self._chunks[i], float(similarities[i])) for i in top_k_indices]
        return results
