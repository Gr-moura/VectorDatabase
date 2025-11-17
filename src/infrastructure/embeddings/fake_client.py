# src/infrastructure/embeddings/fake_client.py

from typing import List, Dict
from .base_client import IEmbeddingsClient
import numpy as np


class FakeEmbeddingsClient(IEmbeddingsClient):
    """
    A fake embeddings client for testing purposes.
    Returns pre-defined vectors for specific texts.
    """

    def __init__(self, dimension: int = 3):
        # We can store our test vectors here, keyed by the text.
        self.known_embeddings: Dict[str, List[float]] = {
            "cat": [0.1, 0.2, 0.8],
            "dog": [0.9, 0.2, 0.1],
            "kitten": [0.15, 0.25, 0.75],
            "puppy": [0.85, 0.25, 0.15],
            "computer": [0.1, 0.9, 0.1],
        }
        self.dimension = dimension

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Looks up texts in the known_embeddings map.
        If a text is not found, it returns a random vector for reproducibility.
        """
        embeddings = []
        for text in texts:
            if text in self.known_embeddings:
                embeddings.append(self.known_embeddings[text])
            else:
                # For unknown texts, generate a consistent but "random" vector
                # based on a hash of the text, so it's always the same.
                seed = hash(text) % (2**32 - 1)
                np.random.seed(seed)
                random_vector = np.random.rand(self.dimension).tolist()
                embeddings.append(random_vector)
        return embeddings
