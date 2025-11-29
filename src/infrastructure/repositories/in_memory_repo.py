# src/infrastructure/repositories/in_memory_repo.py

from typing import Dict, List
from uuid import UUID
from src.core.models import Library
from src.core.exceptions import LibraryNotFound
from .base_repo import ILibraryRepository
from src.infrastructure.concurrency.rwlock import RWLock  # <--- Import


class InMemoryLibraryRepository(ILibraryRepository):
    def __init__(self):
        self._data: Dict[UUID, Library] = {}
        self._lock = RWLock()

    # --- WRITERS (Exclusive Access) ---

    def add(self, library: Library) -> None:
        with self._lock.write_lock():
            if library.uid in self._data:
                return
            self._data[library.uid] = library

    def update(self, library: Library) -> None:
        with self._lock.write_lock():
            if library.uid not in self._data:
                raise LibraryNotFound(f"Library with id {library.uid} not found")
            self._data[library.uid] = library

    def delete(self, library_id: UUID) -> None:
        with self._lock.write_lock():
            if library_id not in self._data:
                raise LibraryNotFound(f"Library with id {library_id} not found")
            del self._data[library_id]

    def clear(self) -> None:
        with self._lock.write_lock():
            self._data.clear()

    # --- READERS (Shared Access) ---

    def get_by_id(self, library_id: UUID) -> Library:
        with self._lock.read_lock():
            library = self._data.get(library_id)
            if not library:
                raise LibraryNotFound(f"Library with id {library_id} not found")
            # Returning a deep copy to prevent external mutations
            return library.model_copy(deep=True)

    def list_all(self) -> List[Library]:
        with self._lock.read_lock():
            return [lib.model_copy(deep=True) for lib in self._data.values()]
