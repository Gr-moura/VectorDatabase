# Vector Database REST API

A containerized REST API acting as a Vector Database. This system allows users to manage Libraries, Documents, and Chunks, generating vector embeddings automatically via Cohere and performing k-Nearest Neighbor (k-NN) searches using custom-implemented indexing algorithms without external vector libraries (like FAISS or Pinecone).

## ✨ Features

  * **Hierarchical Data Management:** Manage **Libraries** containing **Documents**, which contain **Chunks**.
  * **Automatic Embedding Generation:** Integrates with Cohere (v3 models) to generate vector embeddings for text chunks automatically.
  * **Custom Indexing:** Two distinct, custom-coded indexing implementations (AVL Tree and LSH) demonstrating exact vs. approximate search trade-offs.
  * **Vector Search:** Perform k-NN semantic search to find relevant text chunks.
  * **Concurrency Safety:** Custom implementation of Reader-Writer Locks (RWLock) with writer priority and Optimistic Concurrency Control (OCC) to prevent data races and lost updates.
  * **RESTful API:** Endpoints built with FastAPI, adhering to HTTP semantics and response standards.

## 🛠 Tech Stack

  * **Language:** Python 3.13
  * **Framework:** FastAPI (API layer)
  * **Server:** Uvicorn 
  * **Validation:** Pydantic V2
  * **Math/Linear Algebra:** NumPy
  * **Dependency Management:** `uv` 
  * **Containerization:** Docker & Docker Compose

## 🏗 Architecture & Design Choices

### Domain Models

The system follows a hierarchical schema to ensure data integrity. We utilize a **Controller-Service-Repository** pattern to decouple API endpoints from business logic and data access.

1.  **Library:** Holds configuration, metadata, and the runtime indices.
2.  **Document:** Represents a logical grouping of text (e.g., a file).
3.  **Chunk:** The atomic unit of data. Contains the raw text and the float vector (embedding).

### Indexing Algorithms & Complexity

 Two distinct indexing strategies are implemented. Note that `N` is the number of vectors, and `k` is the number of neighbors requested.

#### 1\. AVL Tree Index (Exact Search)

A self-balancing Binary Search Tree keyed by Chunk UUID.

  * **Why this choice?** It provides deterministic performance for CRUD operations, ensuring the index structure remains efficient even with frequent data modifications. For search, it acts as a baseline for "Exact Search" (Brute Force) to guarantee 100% recall.
  * **Space Complexity:** $O(N + k)$
  * **Time Complexity:**
      * **Insert/Delete/Update:** $O(\log N)$ (due to tree rebalancing).
      * **Search:** $O((N + k) \cdot \log k)$
          * We must traverse all $N$ nodes to compute the exact dot product distance.
          * We maintain a Min-Heap of size $k$ to track the top candidates. Each insertion into the heap takes $O(\log k)$.


#### 2\. Locality Sensitive Hashing (LSH) Index (Approximate Search)

An index using Random Projections to hash similar vectors into the same "buckets". Let `L` be the number of hash tables, `C` be the number of candidates per bucket, and `B` be the number of bits per table.

* **Why this choice?** As datasets grow, $O(N)$ search becomes too slow. LSH sacrifices some accuracy (Recall) for speed by only searching candidates in matching hash buckets.
* **Space Complexity:** $O(N \cdot L)$ where $L$ is the number of hash tables.
* **Time Complexity:**
    * **Insert/Delete/Update:** $O(L \cdot B)$.
    * **Search:** $O(L \cdot B + C \log k)$
        * $O(L \cdot B)$ for computing hash codes across `L` tables.
        * Re-ranking computes exact distances for $C$ candidates: $O(C)$.
        * Finding the top $k$ uses a Min-Heap (Priority Queue) to maintain the best candidates during traversal: $O(C \log k)$.


### Concurrency Control

To satisfy the requirement of preventing data races without an external DB:

1.  **Reader-Writer Lock (RWLock):**

      * **Writer Priority:** To prevent writer starvation under heavy read load, new readers are blocked if a writer is waiting in the queue.

2.  **Optimistic Concurrency Control (OCC):**

      * Entities have a `version` field.
      * Update operations check if the version in the repository matches the version being updated. If not, it raises `409 Conflict`, preventing "Lost Update" anomalies where user B overwrites user A's changes silently.

## 🚀 Getting Started

### Prerequisites

  * Docker & Docker Compose
  * A Cohere API Key (Required for embedding generation).

### Running with Docker

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd vector_db_project
    ```

2.  **Create a `.env` file:**

    ```bash
    echo "COHERE_API_KEY=your_actual_api_key_here" > .env
    ```

3.  **Build and Run:**

    ```bash
    docker-compose up --build
    ```

4.  **Access the API:**
    Open your browser to `http://localhost:8000/docs` to view the Swagger UI.

### Running Locally

1.  **Install `uv`:**

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install dependencies:**

    ```bash
    uv sync
    ```

3.  **Set environment variable:**

    ```bash
    export COHERE_API_KEY=your_key_here
    ```

4.  **Run the server:**

    ```bash
    uvicorn src.main:app --reload
    ```

## 📖 API Documentation

Here is a summary of the primary endpoints.

  * **Libraries**
      * `POST /libraries/`: Create a library.
      * `GET /libraries/`: List libraries (paginated).
  * **Documents**
      * `POST /libraries/{id}/documents`: Add a document.
  * **Chunks**
      * `POST /libraries/{lib_id}/documents/{doc_id}/chunks`: Create a text chunk. The backend automatically calls Cohere to generate the embedding.
  * **Indices & Search**
      * `POST /libraries/{id}/index/{name}`: Build an index (Types: `avl`, `lsh`).
      * `POST /libraries/{id}/search/{index_name}`: Perform a search. You can provide `query_text` (automatically embedded) or `query_embedding`.

## 🧪 Testing

The project uses `pytest` for unit and integration testing.

To run tests inside an isolated Docker container (recommended):

```bash
docker-compose -f docker-compose.test.yml up --build --remove-orphans --abort-on-container-exit
```

To run tests locally:

```bash
pytest tests/
```