FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git sqlite3 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml pycefr.py ./
COPY backend/ backend/
COPY scripts/ scripts/

RUN pip install --no-cache-dir ".[dev]" && \
    chmod +x backend/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["backend/docker-entrypoint.sh"]
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
