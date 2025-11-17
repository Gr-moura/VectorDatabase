# src/core/indexing/index_factory.py

from typing import Type, Dict
from .base_index import VectorIndex
from .enums import IndexType, Metric
from .avl_index import AvlIndex


class IndexFactory:
    """A factory for creating vector index instances."""

    _index_classes: Dict[IndexType, Type[VectorIndex]] = {
        IndexType.AVL: AvlIndex,
    }

    @staticmethod
    def create_index(
        index_type: IndexType,
        metric: Metric = Metric.COSINE,
        **kwargs,  # Keeping for future expansion
    ) -> VectorIndex:
        """Creates an instance of the specified vector index."""
        index_class = IndexFactory._index_classes.get(index_type)
        if not index_class:
            raise ValueError(f"Unknown index type: {index_type}")

        elif index_type == IndexType.AVL:
            return index_class(metric=metric)

        return index_class()
