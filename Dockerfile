# Use explicit version tagging for reproducibility
FROM python:3.13-slim-bookworm

# 1. Install uv directly from the official image (Cleaner/Faster than curl script)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 2. System dependencies
# build-essential is kept for compiling C extensions if wheels are missing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to standard convention
WORKDIR /app

# Configure uv:
# - Compile bytecode for faster startup
# - Use copy mode for linking
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 3. Dependency Layer (Cached)
# Copy only manifest files first. Docker will verify if these changed.
# If not, it skips the 'uv sync' step and uses the cache.
COPY pyproject.toml uv.lock ./

# Install dependencies into .venv
# --frozen: Error if lockfile is out of sync
# --no-install-project: Install dependencies only, not the project root yet
RUN uv sync --frozen --no-install-project

# 4. Source Code Layer
# This changes frequently, so it comes after the heavy dependency install
COPY . .

# Final sync to install the project itself (if configured as a package)
RUN uv sync --frozen

# 5. Environment Setup
# Place the virtualenv in the PATH so we can run 'uvicorn' directly
ENV PATH="/app/.venv/bin:$PATH"

# 6. Runtime
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]