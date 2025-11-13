vector_db_project/
├── .dockerignore
├── .gitignore
├── Dockerfile              <-- Requisito: "Create a docker image for the project"
├── README.md               <-- Explicar: "space and time complexity", "Why did you choose this index?", "Explain your design choices"
├── main.py                 <-- Ponto de entrada da API (cria o app FastAPI e roda com uvicorn)
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   │
│   ├── api/                  <-- CAMADA API: "Implement an API layer on top of that logic"
│   │   ├── __init__.py
│   │   ├── dependencies.py     <-- Injeção de dependência do FastAPI (ex: get_library_service)
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── libraries.py    <-- Endpoints CRUD para /libraries
│   │   │   ├── chunks.py       <-- Endpoints CRUD para /libraries/{id}/chunks
│   │   │   └── search.py       <-- Endpoint para /libraries/{id}/search (k-NN)
│   │   └── schemas.py          <-- Modelos Pydantic (Request/Response) para a camada API
│   │
│   ├── core/                 <-- CAMADA DOMAIN: "Domain-Driven design"
│   │   ├── __init__.py
│   │   ├── models.py           <-- "Define the Chunk, Document and Library classes" (Pydantic)
│   │   ├── exceptions.py       <-- Exceções customizadas (ex: LibraryNotFound, IndexNotReady)
│   │   └── indexing/           <-- "Implement two or three indexing algorithms"
│   │       ├── __init__.py
│   │       ├── base_index.py   <-- Interface (ABC) para um índice vetorial
│   │       ├── flat_index.py   <-- Implementação 1: Brute-force (Flat L2/Cosine)
│   │       └── ivf_index.py    <-- Implementação 2: (ex: Inverted File Index - mais complexo)
│   │
│   ├── services/             <-- CAMADA DE SERVIÇO: "Separate API endpoints from business logic using services"
│   │   ├── __init__.py
│   │   ├── library_service.py  <-- Lógica de negócio para "CRUD operations on libraries"
│   │   ├── chunk_service.py    <-- Lógica de negócio para "CRUD operations on ... chunks"
│   │   └── search_service.py   <-- Lógica para "Index the contents" e "Do k-Nearest Neighbor"
│   │
│   ├── infrastructure/       <-- CAMADA DE INFRAESTRUTURA
│   │   ├── __init__.py
│   │   ├── repositories/       <-- "Separate ... from databases using repositories"
│   │   │   ├── __init__.py
│   │   │   ├── base_repo.py    <-- Interfaces dos Repositórios (ex: ILibraryRepository)
│   │   │   └── in_memory_repo.py <-- Implementação do repositório (ex: um dict global)
│   │   │
│   │   ├── persistence/        <-- Extra Point: "Persistence to Disk"
│   │   │   ├── __init__.py
│   │   │   └── file_storage.py <-- Lógica para salvar/carregar o `in_memory_repo` em disco
│   │   │
│   │   └── concurrency/        <-- "ensure that there are no data races"
│   │       ├── __init__.py
│   │       └── locks.py        <-- Implementação de Read-Write Locks (ex: usando threading.RLock)
│   │
│   └── config.py             <-- Configurações (ex: Pydantic BaseSettings)
│
└── tests/                    <-- Requisito: "Testing"
    ├── __init__.py
    ├── test_api/             <-- Testes de integração para os endpoints
    ├── test_services/        <-- Testes unitários para a lógica de negócio
    └── test_core/            <-- Testes unitários para os algoritmos de indexação e modelos