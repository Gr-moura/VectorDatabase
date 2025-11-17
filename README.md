# Vector DB Project

This project implements a simple, in-memory vector database with a RESTful API built using FastAPI.

## Project Structure

The project is organized into distinct layers:

-   **`main.py`**: The main entry point for the FastAPI application. It initializes the app and includes the API routers.
-   **`src/api/`**: The API layer, responsible for handling HTTP requests and responses.
    -   `endpoints/`: Contains the API routers for different resources (libraries, documents, etc.).
    -   `schemas.py`: Pydantic models for request validation and response serialization.
    -   `dependencies.py`: FastAPI dependency injection setup.
-   **`src/services/`**: The Service layer, containing the core business logic. It orchestrates operations between the domain models and the infrastructure layer.
-   **`src/core/`**: The Domain layer, which is the heart of the application.
    -   `models.py`: Core domain models (`Library`, `Document`, `Chunk`).
    -   `exceptions.py`: Custom domain-specific exceptions.
    -   `indexing/`: Vector indexing algorithms and their interfaces.
-   **`src/infrastructure/`**: The Infrastructure layer, responsible for external concerns like databases and concurrency.
    -   `repositories/`: Data persistence logic (e.g., in-memory, database).
-   **`tests/`**: Contains all the tests for the application.

