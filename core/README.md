# core

Shared library for the labs. Empty for now.

It will hold the reusable building blocks that labs import instead of
re-implementing:

- **LLM provider layer** - one interface over OpenAI, Anthropic, local models
- **Vector stores** - pgvector and others behind a common API
- **Evals** - datasets, metrics and judges for measuring lab output
- **Tracing** - observability hooks for LLM calls and agent steps
