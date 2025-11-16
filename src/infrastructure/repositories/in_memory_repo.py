# vector_db_project/src/infrastructure/repositories/in_memory_repo.py

from typing import Dict, List
from uuid import UUID
import threading
from src.core.models import Library
from src.core.exceptions import LibraryNotFound
from .base_repo import ILibraryRepository


class InMemoryLibraryRepository(ILibraryRepository):
    """In-memory repository implementation for storing libraries."""

    def __init__(self):
        self._data: Dict[UUID, Library] = {}
        self._lock = threading.RLock()  # For basic thread safety

    def add(self, library: Library) -> None:
        with self._lock:
            if library.uid in self._data:
                return
            self._data[library.uid] = library

    def get_by_id(self, library_id: UUID) -> Library:
        with self._lock:
            library = self._data.get(library_id)
            if not library:
                raise LibraryNotFound(f"Library with id {library_id} not found")
            return library.model_copy(deep=True)

    def list_all(self) -> List[Library]:
        with self._lock:
            return [lib.model_copy(deep=True) for lib in self._data.values()]

    def update(self, library: Library) -> None:
        with self._lock:
            if library.uid not in self._data:
                raise LibraryNotFound(f"Library with id {library.uid} not found")
            self._data[library.uid] = library

    def delete(self, library_id: UUID) -> None:
        with self._lock:
            if library_id not in self._data:
                raise LibraryNotFound(f"Library with id {library_id} not found")
            del self._data[library_id]

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
