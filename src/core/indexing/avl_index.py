# src/core/indexing/avl_index.py

from uuid import UUID
from typing import List, Tuple, Any, Optional
import numpy as np

from src.core.models import Chunk
from .base_index import VectorIndex
from .enums import IndexType, Metric
from src.core.exceptions import IndexNotReady


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
        self._vector_count = 0  # Keep track of the count

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
        """Performs an exhaustive search over all nodes in the tree."""
        if self.root is None:
            return []

        # 1. Traverse the tree to collect all chunks and vectors
        candidates = []
        self._in_order_traversal(self.root, candidates)

        if not candidates:
            return []

        # 2. Perform brute-force search on the collected candidates
        chunks, vectors = zip(*candidates)
        matrix = np.array(vectors)
        query_vector = np.array(query_embedding, dtype=np.float32)

        if self.metric == Metric.COSINE:
            if np.linalg.norm(query_vector) > 0:
                query_vector /= np.linalg.norm(query_vector)
            scores = np.dot(matrix, query_vector)
            top_k_indices = np.argsort(scores)[-k:][::-1]

        elif self.metric == Metric.EUCLIDEAN:
            distances = np.sum((matrix - query_vector) ** 2, axis=1)
            top_k_indices = np.argsort(distances)[:k]
            scores = np.sqrt(distances[top_k_indices])
        else:
            raise ValueError(f"Unknown metric: {self.metric}")

        # 3. Format and return results
        results = []
        for i in top_k_indices:
            score = scores[i] if self.metric == Metric.EUCLIDEAN else scores[i]
            results.append((chunks[i], float(score)))

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
