# tests/test_core/test_lsh_index.py

import pytest
import numpy as np
from uuid import uuid4
from src.core.models import Chunk
from src.core.indexing.lsh_index import LshIndex

# --- Fixtures ---


@pytest.fixture
def chunk_factory():
    def _create(embedding):
        return Chunk(uid=uuid4(), text="test", embedding=embedding)

    return _create


@pytest.fixture
def lsh_index():
    # 8 bits, 5 tables provides decent recall for testing small datasets
    return LshIndex(num_bits=8, num_tables=5)


# --- Testes de Unidade ---


def test_initialization(lsh_index):
    assert lsh_index.vector_count == 0
    assert lsh_index._num_bits == 8
    assert lsh_index._num_tables == 5
    # Planes shouldn't be initialized until first insert/build
    assert len(lsh_index._planes) == 0


def test_insert_single_chunk(lsh_index, chunk_factory):
    vec = [0.1, 0.2, 0.3]
    chunk = chunk_factory(vec)

    lsh_index.insert(chunk)

    assert lsh_index.vector_count == 1
    # Check internal storage
    assert chunk.uid in lsh_index._chunks
    # Verify planes were initialized
    assert len(lsh_index._planes) == 5
    assert lsh_index._dimension == 3


def test_hashing_consistency(lsh_index, chunk_factory):
    """Vectors that are identical MUST hash to the same bucket in all tables."""
    vec = [0.5, -0.5, 0.5]
    chunk1 = chunk_factory(vec)
    chunk2 = chunk_factory(vec)  # Different UID, same vector

    lsh_index.insert(chunk1)
    lsh_index.insert(chunk2)

    # Check internal hash tables
    for i in range(lsh_index._num_tables):
        # We don't know the hash string, but we can find it
        # There should be exactly one bucket with 2 items
        buckets = list(lsh_index._tables[i].values())
        non_empty_buckets = [b for b in buckets if len(b) > 0]

        assert len(non_empty_buckets) == 1
        bucket_content = non_empty_buckets[0]
        assert chunk1.uid in bucket_content
        assert chunk2.uid in bucket_content


def test_delete_removes_from_all_structures(lsh_index, chunk_factory):
    chunk = chunk_factory([1.0, 0.0, 0.0])
    lsh_index.insert(chunk)
    assert lsh_index.vector_count == 1

    lsh_index.delete(chunk.uid)

    assert lsh_index.vector_count == 0
    assert chunk.uid not in lsh_index._chunks
    assert chunk.uid not in lsh_index._vectors

    # Ensure it's gone from all hash tables
    for table in lsh_index._tables:
        for bucket in table.values():
            assert chunk.uid not in bucket


def test_build_bulk(lsh_index, chunk_factory):
    chunks = [
        chunk_factory([1, 0, 0]),
        chunk_factory([0, 1, 0]),
        chunk_factory([0, 0, 1]),
    ]
    lsh_index.build(chunks)
    assert lsh_index.vector_count == 3
    assert len(lsh_index._planes) == 5


# --- Teste de Acurácia (Recall) ---


def test_search_accuracy_simple(lsh_index, chunk_factory):
    """
    Test if LSH can distinguish between orthogonal vectors (easy case).
    This confirms the core logic works.
    """
    # Create 3 orthogonal vectors (very different)
    target = chunk_factory([1.0, 0.0, 0.0])  # X-axis
    distractor1 = chunk_factory([0.0, 1.0, 0.0])  # Y-axis
    distractor2 = chunk_factory([0.0, 0.0, 1.0])  # Z-axis

    lsh_index.build([target, distractor1, distractor2])

    # Search for a vector very close to target
    query = [0.99, 0.01, 0.0]

    results = lsh_index.search(query, k=1)

    assert len(results) == 1
    found_chunk, score = results[0]

    assert found_chunk.uid == target.uid
    assert score > 0.9  # Should be very high similarity


def test_search_accuracy_dense(lsh_index, chunk_factory):
    """
    Test LSH in a denser cluster. This validates probability.
    We use a fixed seed inside LSH class, so this should be deterministic.
    """
    np.random.seed(42)  # Seed for data generation

    # 1. Target vector
    target_vec = np.array([1.0, 0.0, 0.0])
    target_chunk = chunk_factory(target_vec.tolist())

    # 2. Near neighbor (10 degrees away)
    # Cos(10) ~= 0.98
    angle_rad = np.radians(10)
    neighbor_vec = np.array([np.cos(angle_rad), np.sin(angle_rad), 0.0])
    neighbor_chunk = chunk_factory(neighbor_vec.tolist())

    # 3. Far neighbors (random noise)
    noise_chunks = []
    for _ in range(50):
        # Generate random vectors in 3D
        v = np.random.randn(3)
        v /= np.linalg.norm(v)
        # Ensure they aren't accidentally too close to target
        if np.dot(v, target_vec) < 0.5:
            noise_chunks.append(chunk_factory(v.tolist()))

    all_chunks = [target_chunk, neighbor_chunk] + noise_chunks
    lsh_index.build(all_chunks)

    # Search exactly at the target
    results = lsh_index.search(target_vec.tolist(), k=2)

    # We expect to find the target itself (score 1.0) and the neighbor (score ~0.98)
    # Note: Since LSH is probabilistic, there is a tiny chance this fails if
    # num_tables is too low, but with 5 tables and 10 degrees, it's very robust.

    found_ids = [res[0].uid for res in results]

    assert target_chunk.uid in found_ids
    assert neighbor_chunk.uid in found_ids
