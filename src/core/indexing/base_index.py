# vector_db_project/src/core/indexing/base_index.py

from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
from src.core.models import Chunk


class VectorIndex(ABC):
    @abstractmethod
    def build(self, chunks: List[Chunk]):
        """Builds or rebuilds the index from a list of chunks."""
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], k: int) -> List[Tuple[Chunk, float]]:
        """
        Searches the index for the k-nearest neighbors.
        Returns a list of tuples, each containing the chunk and its similarity score.
        """
        pass
