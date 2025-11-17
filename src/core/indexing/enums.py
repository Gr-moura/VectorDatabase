# src/core/indexing/enums.py
from enum import Enum


class IndexType(str, Enum):
    """Enumeration for the available index types."""

    AVL = "avl"


class Metric(str, Enum):
    """Enumeration for the distance metrics."""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
