# src/infrastructure/embeddings/cohere_client.py

import cohere
from typing import List
from .base_client import IEmbeddingsClient


class CohereClient(IEmbeddingsClient):

    def __init__(self, model_name: str = "embed-english-v3.0"):
        # Use 'None' to lazily initialize the client on first use.
        self._client = None

        # We need to import it here to avoid circular dependencies at startup
        from src.infrastructure.config import COHERE_API_KEY

        self._api_key = COHERE_API_KEY
        self._model_name = model_name

    @property
    def client(self):
        """Lazy initializer for the Cohere client."""
        if self._client is None:
            self._client = cohere.Client(self._api_key)
        return self._client

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Calls the Cohere API to get embeddings for a list of texts.

        Note: The input_type for embed-v3 should be specified based on the use case.
        'search_document' for indexing, 'search_query' for searching.
        This is a simplified example.
        """
        if not texts:
            return []

        response = self.client.embed(
            texts=texts, model=self._model_name, input_type="search_document"
        )
        return response.embeddings
