FROM python:3.12-slim@sha256:3a7b8bbac1f8dfd93a1718505c7ffba7fa7f0d796b0d1d8f96fe37d8755eb0233
# Pinned base (digest = immutable, per PLOS 2026 Tip #3). Rebuild monthly for CVEs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
# System deps (deterministic, no recommends)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.12 \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY experiments/ ./experiments/
COPY tests/ ./tests/
COPY data/ ./data/
RUN useradd -m -u 10001 researcher && chown -R researcher:researcher /app
USER researcher
CMD ["python3", "-m", "pytest", "-q"]
