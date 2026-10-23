# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Build context is the repo root (see docker-compose.yml).
# Copy dependency files (include README for build metadata)
COPY pyproject.toml uv.lock README.md ./

# Install uv
RUN pip install uv

# Install dependencies
RUN uv sync --frozen

# Copy application code (keeps the repo layout so the workspace still resolves)
COPY labs/rag/01-embeddings-similarity ./labs/rag/01-embeddings-similarity

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Run from the lab directory so relative paths (.env, scripts/) resolve as before
WORKDIR /app/labs/rag/01-embeddings-similarity

# Expose port
EXPOSE 8000

# Health check using built-in urllib
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)"

# Run the application
CMD ["uv", "run", "python", "main.py"]
