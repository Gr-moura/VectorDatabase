# src/core/indexing/base_index.py

from abc import ABC, abstractmethod
from typing import List, Tuple, TYPE_CHECKING
from uuid import UUID

from .enums import IndexType, Metric

if TYPE_CHECKING:
    from src.core.models import Chunk


class VectorIndex(ABC):

    @abstractmethod
    def build(self, chunks: List["Chunk"]):
        """Builds the index from a list of chunks."""
        pass

    @abstractmethod
    def search(
        self, query_embedding: List[float], k: int
    ) -> List[Tuple["Chunk", float]]:
        """Searches the index for the k-nearest neighbors."""
        pass

    @property
    @abstractmethod
    def index_type(self) -> IndexType:
        """The type of this index (e.g., 'flat', 'annoy')."""
        pass

    @property
    @abstractmethod
    def metric(self) -> Metric:
        """The distance/similarity metric used by this index."""
        pass

    @property
    @abstractmethod
    def vector_count(self) -> int:
        """The number of vectors currently in the index."""
        pass
