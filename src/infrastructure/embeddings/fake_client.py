from typing import List, Dict
import hashlib
import numpy as np
from .base_client import IEmbeddingsClient


class FakeEmbeddingsClient(IEmbeddingsClient):
    """
    A fake embeddings client for testing purposes.
    Returns pre-defined vectors or deterministically generated ones.
    """

    def __init__(self, dimension: int = 3):
        self.dimension = dimension

        # Base known vectors
        raw_known = {
            "cat": [0.1, 0.2, 0.8],
            "dog": [0.9, 0.2, 0.1],
            "kitten": [0.15, 0.25, 0.75],
            "puppy": [0.85, 0.25, 0.15],
            "computer": [0.1, 0.9, 0.1],
        }

        # Fix 3: Filter known embeddings to ensure dimension consistency
        self.known_embeddings: Dict[str, List[float]] = {}
        for text, vec in raw_known.items():
            if len(vec) == self.dimension:
                self.known_embeddings[text] = vec

    def get_embeddings(
        self, texts: List[str], input_type: str = "search_document"
    ) -> List[List[float]]:
        embeddings = []
        for text in texts:
            if text in self.known_embeddings:
                embeddings.append(self.known_embeddings[text])
            else:
                # Use stable hashing (MD5/SHA) instead of hash()
                # This ensures the same vector across different Python runs/machines
                hash_object = hashlib.md5(text.encode())
                # Create a 32-bit integer seed from the hash
                seed = int(hash_object.hexdigest(), 16) % (2**32 - 1)

                rng = np.random.default_rng(seed)

                random_vector = rng.random(self.dimension).tolist()
                embeddings.append(random_vector)

        return embeddings
