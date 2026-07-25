# Uses uv's official image (uv + Python 3.11 prebuilt) so the build is fully
# deterministic — no Nixpacks/nix resolution, no Python download. Railway
# auto-detects this Dockerfile and builds from it.
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# The slim image ships no CA certificates. main.py uses truststore, which reads
# the OS trust store for outbound HTTPS (e.g. the OpenAI API) — without this,
# every API call fails SSL verification.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (cached layer) from the committed lockfile.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Then copy the application code.
COPY . .

# Railway injects $PORT at runtime; shell form expands it (fallback 8000 local).
CMD uv run uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
