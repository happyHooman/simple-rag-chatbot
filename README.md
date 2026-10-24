# AI Learning Playground

A hands-on playground for learning applied AI by building it. Each **lab** is a small,
runnable project focused on one idea (embeddings, retrieval, agent patterns,
multi-agent architectures, evals, deployment). Labs will gradually share a common
`core/` library so you can swap providers, vector stores and tracing without
rewriting the lab.

> Status: Phase 0. The repo was restructured from a single RAG chatbot; that app now
> lives in Lab 01. Shared components and new labs come next.

## Layout

```
.
├── core/          # shared library (LLM providers, vector stores, evals, tracing) - empty for now
├── labs/          # runnable labs, grouped by track
│   └── rag/
│       └── 01-embeddings-similarity/   # FAQ chatbot: embeddings + pgvector + routing
├── infra/         # Terraform / Kubernetes / deployment material - placeholder
├── docs/
│   └── curriculum.md   # the learning tracks
├── pyproject.toml # single uv project for the whole repo
└── uv.lock
```

See [docs/curriculum.md](docs/curriculum.md) for the planned tracks.

## Running Lab 01

Requirements: Python 3.13+, [uv](https://docs.astral.sh/uv/), Docker.

```bash
# Install dependencies (from the repo root)
uv sync --extra dev

# Everything else runs from the lab folder
cd labs/rag/01-embeddings-similarity
cp .env.example .env        # then set OPENAI_API_KEY, VALID_TOKENS, JWT_SECRET_KEY

docker compose up -d        # app + Postgres/pgvector + Redis + Celery worker
# or, locally: uv run python main.py
```

Full details are in the [lab README](labs/rag/01-embeddings-similarity/README.md).

## Checks

From the repo root:

```bash
uv run ruff check
uv run mypy
uv run pytest
```
