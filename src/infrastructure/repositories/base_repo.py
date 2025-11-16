# vector_db_project/src/infrastructure/repositories/base_repo.py

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from src.core.models import Library


class ILibraryRepository(ABC):
    """Interface for Library repository implementations."""

    @abstractmethod
    def add(self, library: Library) -> None:
        pass

    @abstractmethod
    def get_by_id(self, library_id: UUID) -> Library:
        pass

    @abstractmethod
    def list_all(self) -> List[Library]:
        pass

    @abstractmethod
    def update(self, library: Library) -> None:
        pass

    @abstractmethod
    def delete(self, library_id: UUID) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:  # Helper for testing
        pass
