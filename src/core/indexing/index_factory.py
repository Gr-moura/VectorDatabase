# src/core/indexing/index_factory.py

from typing import Type, Dict
from .base_index import VectorIndex
from .enums import IndexType, Metric
from .avl_index import AvlIndex
from .lsh_index import LshIndex


class IndexFactory:
    """A factory for creating vector index instances."""

    _index_classes: Dict[IndexType, Type[VectorIndex]] = {
        IndexType.AVL: AvlIndex,
        IndexType.LSH: LshIndex,
    }

    @staticmethod
    def create_index(
        index_type: IndexType,
        metric: Metric = Metric.COSINE,
        num_bits: int = 8,
        num_tables: int = 3,
        **kwargs,
    ) -> VectorIndex:
        """Creates an instance of the specified vector index."""
        index_class = IndexFactory._index_classes.get(index_type)
        if not index_class:
            raise ValueError(f"Unknown index type: {index_type}")

        elif index_type == IndexType.AVL:
            return index_class(metric=metric)

        elif index_type == IndexType.LSH:
            return index_class(num_bits=num_bits, num_tables=num_tables)

        return index_class()
