# src/core/indexing/avl_index.py

from uuid import UUID
from typing import List, Tuple, Optional
import numpy as np
import heapq

from src.core.models import Chunk
from .base_index import VectorIndex
from .enums import IndexType, Metric


class AvlNode:
    """A node in the AVL Tree."""

    def __init__(self, chunk: Chunk, vector: np.ndarray):
        self.key: UUID = chunk.uid  # The key for sorting is the chunk's UUID
        self.chunk: Chunk = chunk
        self.vector: np.ndarray = vector
        self.height: int = 1
        self.left: Optional[AvlNode] = None
        self.right: Optional[AvlNode] = None


class AvlIndex(VectorIndex):
    """
    A vector index implemented using a self-balancing AVL tree.
    The tree is balanced based on the chunk UUIDs, providing O(log N) for
    additions, updates, and deletions.
    Search requires a full O(N) traversal of all nodes.
    """

    def __init__(self, metric: Metric = Metric.COSINE):
        self._metric = metric
        self.root: Optional[AvlNode] = None
        self._vector_count = 0

    @property
    def index_type(self) -> IndexType:
        return IndexType.AVL

    @property
    def metric(self) -> Metric:
        return self._metric

    @property
    def vector_count(self) -> int:
        return self._vector_count

    def build(self, chunks: List[Chunk]):
        self.root = None
        self._vector_count = 0
        for chunk in chunks:
            if chunk.embedding:
                self.insert(chunk)

    def insert(self, chunk: Chunk):
        """Inserts a single chunk into the tree."""
        if not chunk.embedding:
            return

        vector = np.array(chunk.embedding, dtype=np.float32)
        if self.metric == Metric.COSINE:
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector /= norm

        self.root = self._insert_node(self.root, chunk, vector)

    def delete(self, chunk_id: UUID):
        """Deletes a single chunk from the tree by its UUID."""
        if self.root:
            self.root = self._delete_node(self.root, chunk_id)

    def search(self, query_embedding: List[float], k: int) -> List[Tuple[Chunk, float]]:
        """
        Performs an exhaustive search over all nodes in the tree using a Heap.

        This implementation uses a Priority Queue (heapq) to maintain only the
        top-k candidates during traversal. This is memory efficient O(k) but
        less CPU efficient than fully vectorized NumPy operations for large datasets.
        """
        if self.root is None:
            return []

        query_vector = np.array(query_embedding, dtype=np.float32)

        # Pre-process query vector based on metric
        if self.metric == Metric.COSINE:
            norm = np.linalg.norm(query_vector)
            if norm > 0:
                query_vector /= norm

        # Min-heap to store tuples of (score_priority, chunk).
        # Python's heapq is a min-heap (pops the smallest value).
        candidates_heap = []

        def _visit_node(node: Optional[AvlNode]):
            if not node:
                return

            # 1. Calculate score for the current node
            vector = node.vector

            if self.metric == Metric.COSINE:
                # Cosine Similarity (Dot product of normalized vectors).
                # Higher is better.
                # We want to keep the K largest values.
                # If we push the score directly, heappop will remove the SMALLEST score.
                # This leaves us with the largest scores in the heap.
                score = float(np.dot(vector, query_vector))
                heapq.heappush(candidates_heap, (score, node.chunk))

            elif self.metric == Metric.EUCLIDEAN:
                # Euclidean Distance.
                # Lower is better.
                # We want to keep the K smallest values.
                # We need to simulate a Max-Heap to pop the LARGEST distance (the worst candidate).
                # We store -distance. The "smallest" number is the one with largest magnitude (e.g. -10 < -2).
                # heappop will remove -10 (distance 10), keeping -2 (distance 2).
                dist = float(np.linalg.norm(vector - query_vector))
                heapq.heappush(candidates_heap, (-dist, node.chunk))

            # 2. Maintain heap size
            if len(candidates_heap) > k:
                heapq.heappop(candidates_heap)

            # 3. Continue traversal
            _visit_node(node.left)
            _visit_node(node.right)

        # Start the recursive traversal
        _visit_node(self.root)

        # 4. Sort and Format Results
        results = []

        if self.metric == Metric.COSINE:
            # The heap contains the top-k, but unsorted.
            # Sort descending by score (highest similarity first).
            sorted_candidates = sorted(
                candidates_heap, key=lambda x: x[0], reverse=True
            )
            for score, chunk in sorted_candidates:
                results.append((chunk, score))

        elif self.metric == Metric.EUCLIDEAN:
            # The heap contains (-distance, chunk).
            # Sort descending by the negative distance (e.g. -2, -5, -10).
            # This corresponds to distances 2, 5, 10.
            sorted_candidates = sorted(
                candidates_heap, key=lambda x: x[0], reverse=True
            )
            for neg_dist, chunk in sorted_candidates:
                # Convert back to positive distance
                results.append((chunk, -neg_dist))

        return results

    # --- AVL Tree Core Logic ---

    def _insert_node(
        self, node: Optional[AvlNode], chunk: Chunk, vector: np.ndarray
    ) -> AvlNode:
        # 1. Standard Binary Search Tree insertion
        if not node:
            self._vector_count += 1
            return AvlNode(chunk, vector)
        elif chunk.uid < node.key:
            node.left = self._insert_node(node.left, chunk, vector)
        elif chunk.uid > node.key:
            node.right = self._insert_node(node.right, chunk, vector)
        else:  # Key already exists, perform an update
            node.chunk = chunk
            node.vector = vector
            return node

        # 2. Update height of the ancestor node
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # 3. Get the balance factor and perform rotations if needed
        balance = self._get_balance(node)

        # Case 1: Left Left
        if balance > 1 and chunk.uid < node.left.key:
            return self._right_rotate(node)

        # Case 2: Right Right
        if balance < -1 and chunk.uid > node.right.key:
            return self._left_rotate(node)

        # Case 3: Left Right
        if balance > 1 and chunk.uid > node.left.key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Case 4: Right Left
        if balance < -1 and chunk.uid < node.right.key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _left_rotate(self, z: AvlNode) -> AvlNode:
        y = z.right
        T2 = y.left
        y.left = z
        z.right = T2
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _right_rotate(self, z: AvlNode) -> AvlNode:
        y = z.left
        T3 = y.right
        y.right = z
        z.left = T3
        z.height = 1 + max(self._get_height(z.left), self._get_height(z.right))
        y.height = 1 + max(self._get_height(y.left), self._get_height(y.right))
        return y

    def _get_min_value_node(self, node: AvlNode) -> AvlNode:
        """Finds the node with the smallest key (leftmost) in a subtree."""
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _delete_node(self, node: Optional[AvlNode], key: UUID) -> Optional[AvlNode]:
        # 1. Standard Binary Search Tree deletion
        if not node:
            return node
        elif key < node.key:
            node.left = self._delete_node(node.left, key)
        elif key > node.key:
            node.right = self._delete_node(node.right, key)
        else:  # Node to be deleted found
            self._vector_count -= 1  # Decrement the counter
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Node with two children: get the in-order successor (smallest in the right subtree)
            temp = self._get_min_value_node(node.right)
            node.key = temp.key
            node.chunk = temp.chunk
            node.vector = temp.vector
            node.right = self._delete_node(node.right, temp.key)

        if not node:
            return node

        # 2. Update the height and rebalance the tree (same logic as insertion)
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)

        # Rotations to rebalance

        # Left Left
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)
        # Left Right
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        # Right Right
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)
        # Right Left
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _get_height(self, node: Optional[AvlNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AvlNode]) -> int:
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _in_order_traversal(
        self, node: Optional[AvlNode], result_list: List[Tuple[Chunk, np.ndarray]]
    ):
        """Recursively traverses the tree to collect all nodes."""
        if not node:
            return
        self._in_order_traversal(node.left, result_list)
        result_list.append((node.chunk, node.vector))
        self._in_order_traversal(node.right, result_list)
