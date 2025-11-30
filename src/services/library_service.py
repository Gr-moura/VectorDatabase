# vector_db_project/src/services/library_service.py

from uuid import UUID
from typing import List
from src.core.models import Library
from src.api.schemas import LibraryCreate, LibraryUpdate
from src.infrastructure.repositories.base_repo import ILibraryRepository


class LibraryService:
    def __init__(self, repository: ILibraryRepository):
        self.repository = repository

    def create_library(self, library_create: LibraryCreate) -> Library:
        library = Library(**library_create.model_dump())
        self.repository.add(library)
        return library

    def get_library(self, library_id: UUID) -> Library:
        return self.repository.get_by_id(library_id)

    def update_library(
        self, library_id: UUID, library_update: LibraryUpdate
    ) -> Library:
        library = self.repository.get_by_id(library_id)

        # 1. Get current data
        current_data = library.model_dump()

        # 2. Merge with update data
        update_data = library_update.model_dump(exclude_unset=True)
        current_data.update(update_data)

        # 3. Create new instance to enforce validation rules
        updated_library = Library(**current_data)

        self.repository.update(updated_library)
        return updated_library

    def delete_library(self, library_id: UUID) -> None:
        self.repository.delete(library_id)

    def list_libraries(self) -> List[Library]:
        return self.repository.list_all()
