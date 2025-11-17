FROM python:3.13-slim-bookworm

# Install build-essential (for `uv sync` building sdist)
# and curl (for the `uv` installer script).
RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        curl && \
    # Clean apt cache
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add the installer script
ADD https://astral.sh/uv/install.sh /install.sh

# Run the installer, then remove the script and curl in the same layer.
# Using `chmod +x` is correct for a single file.
RUN chmod +x /install.sh && \
    /install.sh && \
    rm /install.sh && \
    # Clean up curl, which is no longer needed
    apt-get purge -y --auto-remove curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up the UV environment path correctly
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /src

COPY . .

# Install dependencies
RUN uv sync

ENV PATH="/src/.venv/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]