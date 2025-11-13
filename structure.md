 project_root/
├─ app/
│  ├─ main.py                # FastAPI app + route registration
│  ├─ api/                   # endpoints (thin controllers)
│  ├─ services/              # business logic (indexing, CRUD)
│  ├─ repositories/          # persistence (JSON/SQLite)
│  ├─ models/                # Pydantic models + domain classes
│  ├─ indexes/               # implementations de index (linear, kdtree, lsh)
│  ├─ concurrency/           # locks, versioning utilities
│  └─ utils/                 # vector ops, metrics
├─ tests/                    # pytest tests
├─ Dockerfile
├─ pyproject.toml / requirements.txt
└─ README.md