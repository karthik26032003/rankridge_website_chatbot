# Uses uv's official image (uv + Python 3.11 prebuilt) so the build is fully
# deterministic — no Nixpacks/nix resolution, no Python download. Railway
# auto-detects this Dockerfile and builds from it.
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Install dependencies first (cached layer) from the committed lockfile.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Then copy the application code.
COPY . .

# Railway injects $PORT at runtime; shell form expands it (fallback 8000 local).
CMD uv run uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
