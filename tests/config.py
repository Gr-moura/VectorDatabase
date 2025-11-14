import pytest
from services import LibraryService


@pytest.fixture()
def service():
    # fresh isolated instance for each test
    return LibraryService()


@pytest.fixture()
def sample_library_id(service):
    return service.create_library("TestLib")


@pytest.fixture()
def sample_document_id(service, sample_library_id):
    return service.create_document(sample_library_id, name="Doc1", text="Base text")
