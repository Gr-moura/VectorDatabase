import cohere
from typing import List, Optional
from .base_client import IEmbeddingsClient

# Removed internal config import in favor of top-level or injection


class CohereClient(IEmbeddingsClient):
    # Batch limit for Cohere API
    BATCH_SIZE = 96

    def __init__(
        self,
        api_key: str,  # Dependency Injection: Pass key here; do not import internally
        model_name: str = "embed-english-v3.0",
    ):
        self._api_key = api_key
        self._model_name = model_name
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = cohere.Client(self._api_key)
        return self._client

    def get_embeddings(
        self,
        texts: List[str],
        input_type: str = "search_document",  # Default for indexing; override for search
    ) -> List[List[float]]:
        if not texts:
            return []

        all_embeddings = []

        for i in range(0, len(texts), self.BATCH_SIZE):
            batch = texts[i : i + self.BATCH_SIZE]

            try:
                response = self.client.embed(
                    texts=batch, model=self._model_name, input_type=input_type
                )
                all_embeddings.extend(response.embeddings)
            except Exception as e:
                # Log error and re-raise or handle per resiliency policy
                raise ConnectionError(
                    f"Cohere API failed on batch {i}: {str(e)}"
                ) from e

        return all_embeddings
