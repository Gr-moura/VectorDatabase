# Vector DB Project

This project implements a simple, in-memory vector database with a RESTful API built using FastAPI. It follows a clean, layered architecture inspired by Domain-Driven Design (DDD) to promote separation of concerns, testability, and maintainability.

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

## Design Choices

-   **Layered Architecture**: We chose a layered architecture (API -> Service -> Repository -> Core) to decouple different parts of the application. The API layer knows about services, services know about repositories and the domain, but the domain layer knows nothing about the outer layers. This makes it easy to change the database or API framework without affecting the core business logic.
-   **Dependency Injection**: FastAPI's dependency injection system is used extensively to provide services and repositories to the API endpoints. This makes testing much easier, as we can inject mock dependencies instead of real ones. The `dependencies.py` file centralizes the creation of these components.
-   **Repository Pattern**: This pattern abstracts the data storage mechanism. The services interact with a repository `interface` (`ILibraryRepository`), not a concrete implementation. This means we can switch from the current `InMemoryLibraryRepository` to a `PostgresRepository` with minimal changes to the service layer.
-   **Pydantic for Models**: Pydantic is used for both core domain models and API schemas. This ensures data validation and consistency from the API boundary all the way down to the domain logic.

## Indexing Algorithm Choice

For this project, I implemented a **Brute-Force (Flat) Index**.

-   **Why this index?**
    -   **Simplicity and Correctness**: It is the simplest possible vector search algorithm. It calculates the distance (or similarity) between the query vector and every other vector in the dataset. This guarantees that it will always find the exact nearest neighbors.
    -   **Baseline**: It serves as an excellent, perfectly accurate baseline to which more complex, approximate nearest neighbor (ANN) algorithms can be compared.
    -   **Good for Small Datasets**: For small numbers of vectors (thousands to tens of thousands), a brute-force search is often fast enough and avoids the complexity and overhead of building a more advanced index.

-   **Space and Time Complexity**
    -   **Space Complexity**: `O(N * D)`, where `N` is the number of vectors and `D` is the dimensionality of each vector. We simply need to store all the vectors in memory.
    -   **Query Time Complexity**: `O(N * D)`. To find the nearest neighbors for a single query, we must perform `N` distance calculations, and each calculation takes `O(D)` time. The complexity is linear with respect to the number of vectors in the index.

-   **When to use a different index?**
    -   The `O(N * D)` query time of a flat index becomes a major bottleneck as `N` grows into the millions or billions. In such cases, an **Approximate Nearest Neighbor (ANN)** algorithm like **IVF (Inverted File Index)** or **HNSW (Hierarchical Navigable Small Worlds)** would be a better choice. These algorithms trade a small amount of accuracy for a massive speedup in query time, often achieving `O(log N)` or `O(polylog N)` complexity. The `src/core/indexing/` structure is designed to easily accommodate adding these new index types.