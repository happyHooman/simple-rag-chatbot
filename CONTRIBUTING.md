# Contributing

Thanks for helping build the AI Learning Playground! The goal is a set of small,
runnable labs that teach applied AI by doing: RAG, agent patterns, multi-agent
systems, evals and ops. See [docs/curriculum.md](docs/curriculum.md) for the tracks.

## Setup

Requirements: Python 3.13+, [uv](https://docs.astral.sh/uv/), and Docker for labs
that need services.

```bash
uv sync --extra dev
uv run pytest           # runs offline: no API keys, .env or services needed
uv run pytest --live    # also runs tests against real OpenAI/Postgres/Redis/Docker
```

Lab-specific instructions live in each lab's README (e.g.
[Lab 01](labs/rag/01-embeddings-similarity/README.md)).

## How a lab is structured

Each lab lives in `labs/<track>/<NN-short-name>/` and should contain:

- **README.md**: the goal, the concepts it teaches, step-by-step instructions, and
  what "done" looks like.
- **Runnable code**: a minimal working implementation the learner can run and modify.
- **Config knobs**: the parameters worth experimenting with (models, chunk size,
  top-k, thresholds...), exposed via `.env.example` or config, not hard-coded.
- **Evals**: a way to measure whether a change made things better (tests, a small
  dataset, or an eval script).
- **CHALLENGES.md**: exercises that extend the lab, from easy to hard.
- **solution/**: reference solutions for the challenges.

Shared building blocks (LLM providers, vector stores, evals, tracing) belong in
`core/`, not copied between labs.

## Workflow

1. Fork the repo and create a branch from `main`.
2. Keep PRs small: one lab or one focused change per PR.
3. Make sure `uv run pytest` passes offline. New code should come with tests that
   don't need API keys (use fakes, see `labs/rag/01-embeddings-similarity/tests/conftest.py`);
   mark tests that need real services with `@pytest.mark.live`.
4. Update the relevant README/docs.
5. Open a PR and fill in the template. `main` is protected: every PR needs one
   approving review and all review threads resolved.

**Never commit `.env` files, API keys or tokens.** Use `.env.example` with
placeholder values.

## Proposing a new lab

Open a [Lab proposal](https://github.com/happyHooman/simple-rag-chatbot/issues/new?template=lab_proposal.yml) issue before
writing code, so we can agree on scope and where it fits in the curriculum.
Good first contributions are tagged
[`good first issue`](https://github.com/happyHooman/simple-rag-chatbot/labels/good%20first%20issue).

## Questions

Use [Discussions](https://github.com/happyHooman/simple-rag-chatbot/discussions) for questions and ideas. Please follow the
[Code of Conduct](CODE_OF_CONDUCT.md).
