# src/core/indexing/lsh_index.py

from uuid import UUID
from typing import List, Tuple, Dict, Set, Optional
import numpy as np

from src.core.models import Chunk
from .base_index import VectorIndex
from .enums import IndexType, Metric
from src.core.exceptions import IndexNotReady


class LshIndex(VectorIndex):
	"""
	Locality Sensitive Hashing (LSH) using Random Projections.
	Best for Cosine Similarity. Supports dynamic updates.
	"""

	def __init__(
		self, num_bits: int = 8, num_tables: int = 3, seed: Optional[int] = None
	):
		"""
		Args:
						num_bits: Number of hyperplanes per table. Higher = fewer collisions (precision), lower recall.
						num_tables: Number of independent hash tables. Higher = higher recall, more memory.
						seed: Optional seed for reproducibility. If None, uses entropy from OS.
		"""
		self._num_bits = num_bits
		self._num_tables = num_tables
		self._metric = Metric.COSINE

		self._rng = np.random.default_rng(seed)

		# List of hyperplanes (random normal vectors) for each table
		# Shape per table: (dimension, num_bits)
		self._planes: List[np.ndarray] = []

		# List of hash tables. Each table maps a hash string to a list of chunk UUIDs
		self._tables: List[Dict[str, Set[UUID]]] = []

		# Storage for the actual vectors/chunks for re-ranking
		self._chunks: Dict[UUID, Chunk] = {}
		self._vectors: Dict[UUID, np.ndarray] = {}
		self._dimension: int = 0

	@property
	def index_type(self) -> IndexType:
		return IndexType.LSH

	@property
	def metric(self) -> Metric:
		return self._metric

	@property
	def vector_count(self) -> int:
		return len(self._chunks)

	def _initialize_planes(self, dimension: int):
		"""Initializes random hyperplanes if not already done."""
		if not self._planes:
			self._dimension = dimension

			for _ in range(self._num_tables):
				# Create random vectors from normal distribution
				planes = self._rng.standard_normal((dimension, self._num_bits))
				self._planes.append(planes)
				self._tables.append({})

	def _hash_vector(self, vector: np.ndarray, table_index: int) -> str:
		"""Computes the hash signature (bit string) for a vector in a specific table."""
		# Projection: dot product determines which side of the hyperplane the vector is on
		# Result shape: (num_bits,)
		projections = np.dot(vector, self._planes[table_index])

		# Convert to bits: 1 if > 0, else 0
		bits = (projections > 0).astype(int)

		# Convert numpy array of bits to a string "1010..."
		return "".join(bits.astype(str))

	def build(self, chunks: List[Chunk]):
		"""Bulk build."""
		# 1. Clear existing data
		self._chunks.clear()
		self._vectors.clear()
		self._planes.clear()
		self._tables.clear()
		self._dimension = 0

		valid_chunks = [c for c in chunks if c.embedding]
		if not valid_chunks:
			return

		# Initialize dimensions based on the first vector
		dim = len(valid_chunks[0].embedding)
		self._initialize_planes(dim)

		for chunk in valid_chunks:
			self.insert(chunk)

	def insert(self, chunk: Chunk):
		"""Adds a single chunk to the index dynamically."""
		if not chunk.embedding:
			return

		vector = np.array(chunk.embedding, dtype=np.float32)
		# Normalize for Cosine LSH (Random Projection works on angle)
		norm = np.linalg.norm(vector)
		if norm > 0:
			vector /= norm

		# Check dimension consistency
		if self._dimension == 0:
			self._initialize_planes(len(vector))
		elif len(vector) != self._dimension:
			# Skip vectors of wrong dimension to avoid crashing
			return

		# Store data
		self._chunks[chunk.uid] = chunk
		self._vectors[chunk.uid] = vector

		# Index into each table
		for i in range(self._num_tables):
			signature = self._hash_vector(vector, i)
			if signature not in self._tables[i]:
				self._tables[i][signature] = set()
			self._tables[i][signature].add(chunk.uid)

	def delete(self, chunk_id: UUID):
		"""Removes a chunk from the index."""
		if chunk_id not in self._vectors:
			return

		vector = self._vectors[chunk_id]

		# Remove from all tables
		for i in range(self._num_tables):
			signature = self._hash_vector(vector, i)
			if signature in self._tables[i]:
				self._tables[i][signature].discard(chunk_id)
				# Cleanup empty buckets to save memory
				if not self._tables[i][signature]:
					del self._tables[i][signature]

		# Remove storage
		self._chunks.pop(chunk_id, None)
		self._vectors.pop(chunk_id, None)

	def search(self, query_embedding: List[float], k: int) -> List[Tuple[Chunk, float]]:
		"""
		Approximate search:
		1. Hash query vector.
		2. Collect candidates from matching buckets in all tables.
		3. Brute-force re-rank candidates.
		"""
		if not self._planes or not self._vectors:
			return []

		query_vector = np.array(query_embedding, dtype=np.float32)
		norm = np.linalg.norm(query_vector)
		if norm > 0:
			query_vector /= norm

		# 1. Collect Candidates
		candidate_ids: Set[UUID] = set()
		for i in range(self._num_tables):
			signature = self._hash_vector(query_vector, i)
			# Add all IDs found in this bucket
			bucket_ids = self._tables[i].get(signature, set())
			candidate_ids.update(bucket_ids)

		if not candidate_ids:
			return []

		# 2. Re-rank Candidates (Exact distance on the subset)
		candidates = list(candidate_ids)
		candidate_matrix = np.array([self._vectors[uid] for uid in candidates])

		# Cosine similarity
		scores = np.dot(candidate_matrix, query_vector)

		# Sort top k
		if len(scores) < k:
			top_indices = np.argsort(scores)[::-1]
		else:
			# argpartition is faster for finding top k without full sort
			top_indices = np.argpartition(scores, -k)[-k:]
			# Sort the top k
			top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

		# 3. Format Results
		results = []
		for idx in top_indices:
			uid = candidates[idx]
			score = scores[idx]
			results.append((self._chunks[uid], float(score)))

		return results
