# src/infrastructure/embeddings/base_client.py

from abc import ABC, abstractmethod
from typing import List


class IEmbeddingsClient(ABC):

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Takes a list of texts and returns a list of their embedding vectors.
        """
        pass
