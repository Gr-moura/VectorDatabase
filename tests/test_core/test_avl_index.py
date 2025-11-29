# tests/test_core/test_avl_index.py

import pytest
import numpy as np
from uuid import uuid4
from src.core.models import Chunk
from src.core.indexing.avl_index import AvlIndex, AvlNode
from src.core.indexing.enums import Metric

# --- Fixtures ---


@pytest.fixture
def chunk_factory():
    def _create(embedding, uid=None):
        return Chunk(uid=uid or uuid4(), text="test", embedding=embedding)

    return _create


@pytest.fixture
def avl_index():
    return AvlIndex(metric=Metric.COSINE)


# --- Helper Functions ---


def is_balanced(node: AvlNode) -> bool:
    """Recursively checks if the tree rooted at node is balanced."""
    if not node:
        return True

    left_height = node.left.height if node.left else 0
    right_height = node.right.height if node.right else 0

    if abs(left_height - right_height) > 1:
        return False

    return is_balanced(node.left) and is_balanced(node.right)


# --- Testes de Unidade ---


def test_initialization(avl_index):
    assert avl_index.vector_count == 0
    assert avl_index.root is None
    assert avl_index.metric == Metric.COSINE


def test_insert_single_chunk(avl_index, chunk_factory):
    chunk = chunk_factory([0.1, 0.2])
    avl_index.insert(chunk)

    assert avl_index.vector_count == 1
    assert avl_index.root is not None
    assert avl_index.root.key == chunk.uid
    assert is_balanced(avl_index.root)


def test_insert_duplicate_updates_chunk(avl_index, chunk_factory):
    uid = uuid4()
    chunk1 = chunk_factory([0.1, 0.1], uid=uid)
    chunk2 = chunk_factory([0.9, 0.9], uid=uid)  # Same UID, different vector

    avl_index.insert(chunk1)
    assert avl_index.vector_count == 1
    assert avl_index.root.vector[0] == pytest.approx(
        0.707, 0.01
    )  # Normalized [0.1, 0.1]

    # Insert update
    avl_index.insert(chunk2)
    assert avl_index.vector_count == 1
    assert avl_index.root.vector[0] == pytest.approx(
        0.707, 0.01
    )  # Normalized [0.9, 0.9] is same direction!

    # Let's try with a different vector direction
    chunk3 = chunk_factory([1.0, 0.0], uid=uid)
    avl_index.insert(chunk3)
    assert avl_index.root.vector[0] == pytest.approx(1.0)


def test_delete_leaf_node(avl_index, chunk_factory):
    c1 = chunk_factory([1, 0], uid=uuid4())
    avl_index.insert(c1)

    avl_index.delete(c1.uid)
    assert avl_index.vector_count == 0
    assert avl_index.root is None


def test_delete_node_with_two_children(avl_index, chunk_factory):
    """
    Test deleting a node that has both left and right children.
    This triggers the successor logic.
    """
    # Create UIDs explicitly to control tree structure (based on UUID comparison)
    # We need a root, a smaller child (left), and a larger child (right)
    # Since UUIDs are random, we sort them first.
    uids = sorted([uuid4() for _ in range(3)])
    mid_uid, min_uid, max_uid = uids[1], uids[0], uids[2]

    root_chunk = chunk_factory([1, 0], uid=mid_uid)
    left_chunk = chunk_factory([0, 1], uid=min_uid)
    right_chunk = chunk_factory([0, 0], uid=max_uid)

    avl_index.insert(root_chunk)
    avl_index.insert(left_chunk)
    avl_index.insert(right_chunk)

    assert avl_index.vector_count == 3
    assert avl_index.root.key == mid_uid

    # Delete the root
    avl_index.delete(mid_uid)

    assert avl_index.vector_count == 2
    # The root should have been replaced by the successor (min of right subtree)
    # In this simple case, the right child becomes root
    assert avl_index.root.key == max_uid
    assert is_balanced(avl_index.root)


def test_avl_balancing_logic(avl_index, chunk_factory):
    """
    Insert nodes in sorted order (worst case for BST).
    Verify that AVL tree keeps height logarithmic (balanced).
    """
    # Create 100 chunks with sorted UIDs
    uids = sorted([uuid4() for _ in range(100)])
    chunks = [chunk_factory([1, 0], uid=uid) for uid in uids]

    for chunk in chunks:
        avl_index.insert(chunk)

    assert avl_index.vector_count == 100
    assert is_balanced(avl_index.root)

    # Height of a balanced tree with 100 nodes should be around log2(100) ~= 7
    # An unbalanced BST would have height 100.
    assert avl_index.root.height < 10


def test_search_accuracy_cosine(avl_index, chunk_factory):
    """Test exact search with Cosine Similarity."""
    target = chunk_factory([1.0, 0.0])  # X-axis
    far = chunk_factory([0.0, 1.0])  # Y-axis (orthogonal, sim=0)
    near = chunk_factory([0.9, 0.1])  # Close to X-axis

    avl_index.build([target, far, near])

    # Search for exactly the target vector
    results = avl_index.search([1.0, 0.0], k=2)

    assert len(results) == 2

    # 1st result: target itself (sim=1.0)
    assert results[0][0].uid == target.uid
    assert results[0][1] == pytest.approx(1.0)

    # 2nd result: near vector
    assert results[1][0].uid == near.uid
    assert results[1][1] > 0.0


def test_search_accuracy_euclidean(chunk_factory):
    """Test exact search with Euclidean Distance."""
    # Create index explicitly with Euclidean metric
    avl_index = AvlIndex(metric=Metric.EUCLIDEAN)

    target = chunk_factory([0, 0])
    close = chunk_factory([0, 1])  # dist = 1
    far = chunk_factory([0, 10])  # dist = 10

    avl_index.build([target, far, close])

    # Search for [0,0]
    results = avl_index.search([0, 0], k=2)

    assert len(results) == 2

    # 1st result: target itself (dist=0)
    assert results[0][0].uid == target.uid
    assert results[0][1] == 0.0

    # 2nd result: close vector (dist=1)
    assert results[1][0].uid == close.uid
    assert results[1][1] == 1.0


def test_search_empty_index_returns_empty(avl_index):
    results = avl_index.search([1, 1], k=5)
    assert results == []
