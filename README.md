# RebelDot Chatbot

An intelligent FAQ assistant powered by FastAPI, OpenAI embeddings, and semantic search. Features AI-powered question routing, background task processing with Celery, and comprehensive monitoring tools.

## ✨ Key Features

- **🤖 AI-Powered FAQ System** - Semantic search using OpenAI embeddings and pgvector
- **🎯 Smart Routing** - LangChain-based classification (IT questions vs. compliance)
- **⚡ Background Tasks** - Asynchronous embeddings processing with Celery + Redis
- **📊 Real-time Monitoring** - Flower dashboard for task visualization
- **🏥 Health Monitoring** - Comprehensive health checks for all services
- **🔐 Secure** - Token-based authentication with FastAPI security

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Docker & Docker Compose
- `uv` package manager
- Redis (for Celery task queue)

### Installation
```bash
# Install dependencies (production)
uv sync

# Install with dev dependencies (includes Flower)
uv sync --extra dev

# Start all services (FastAPI, PostgreSQL, Redis, Celery Worker)
docker compose up -d

# Start with dev tools (includes Adminer and Flower)
docker compose --profile dev up -d
```

## 📋 Available Commands

### Development
```bash
# Start server
uv run python main.py

# Run all tests
uv run pytest tests/ -v

# Run sanity tests (prebuild)
uv run python scripts/prebuild.py
```

### Code Quality
```bash
# Linting
uv run ruff check app/

# Format code
uv run ruff format app/

# Type checking
uv run mypy app/
```

### Docker Services
```bash
# Start all production services (app, postgres, redis, celery worker)
docker compose up -d

# Start with dev tools (+ adminer, flower)
docker compose --profile dev up -d

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f celery_worker

# Stop all services
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

### Background Tasks (Celery)
```bash
# View Celery worker logs
docker compose logs -f celery_worker

# Monitor tasks with Flower (dev profile only)
# Access at http://localhost:5555
docker compose --profile dev up -d
```

## 📡 API Endpoints

### Core Endpoints
- **GET /health** - Overall system status (public)
- **GET /docs** - Interactive API documentation (Swagger UI)
- **POST /ask-question** - FAQ question answering (authenticated)

### Background Task Endpoints
- **POST /generate-embeddings** - Generate all FAQ embeddings (async, authenticated)
  - Returns immediately with `task_id`
  - Processes all FAQ items in background
- **POST /update-embeddings** - Update embeddings incrementally (async, authenticated)
  - Returns immediately with `task_id`
  - Adds/updates/removes embeddings based on changes
- **GET /tasks/{task_id}** - Check task status and result (authenticated)
  - Monitor background task progress
  - Retrieve task results when complete

## 🧪 Testing

### Quick Test
```bash
# Run all tests
uv run pytest tests/ -v

# Run prebuild checks (linting, type checking, sanity tests)
uv run python scripts/prebuild.py
```

### Test Categories
- **Sanity tests** - System readiness checks
- **Unit tests** - Component-level testing
- **Integration tests** - End-to-end API testing
- **Auth tests** - Authentication and authorization
- **AI Router tests** - Question classification logic

## 🔧 Configuration

Environment variables (see `.env.example`):

### API Settings
- `API_TITLE`, `API_VERSION`, `API_DESCRIPTION`
- `HOST`, `PORT`, `LOG_LEVEL`
- `VALID_TOKENS` - Comma-separated authentication tokens

### Database
- `DATABASE_URL` - PostgreSQL connection string
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

### Redis & Celery
- `REDIS_URL` - Redis connection (default: redis://localhost:6379/0)
- `CELERY_BROKER_URL` - Celery broker (uses Redis)
- `CELERY_RESULT_BACKEND` - Result backend (uses Redis)
- `CELERY_TASK_TIME_LIMIT` - Max task duration (default: 1800s)

### OpenAI & AI Settings
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `SIMILARITY_THRESHOLD` - Vector similarity threshold (default: 0.5)
- `OPENAI_CHAT_MODEL` - Chat model (default: gpt-4o-mini)
- `OPENAI_CHAT_TEMPERATURE` - Model temperature (default: 0.3)

## 📊 Monitoring & Health

### Health Endpoint
```bash
curl http://localhost:8000/health
```

**Status Indicators:**
- **operational** - All services healthy
- **degraded** - Some services unavailable

**Monitored Services:**
- Docker container status
- PostgreSQL connection & pgvector extension
- Redis connection
- Embeddings availability

### Development Tools

**Flower Dashboard** (http://localhost:5555)
- Real-time Celery task monitoring
- Worker health and statistics
- Task execution history and timing
- Only available with `--profile dev`

**Adminer Database UI** (http://localhost:8080)
- Visual PostgreSQL database management
- SQL query editor
- Table browser and data inspection
- Only available with `--profile dev`

## 🐳 Docker Deployment

### Quick Start with Docker

#### Option 1: Automated Setup
```bash
./scripts/docker-setup.sh
```

#### Option 2: Manual Setup
```bash
# 1. Create .env file with your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Start services (production)
docker-compose up --build -d

# 2a. Start with development tools (includes Adminer DB admin)
docker-compose --profile dev up --build -d

# 3. Check status
docker-compose ps
```

### Docker Architecture

**Core Services (Production):**
- **rebeldot_app** - FastAPI application on port 8000
- **rebeldot_postgres** - PostgreSQL + pgvector on port 5432
- **rebeldot_redis** - Redis cache/broker on port 6379
- **rebeldot_celery_worker** - Background task processor (Celery)

**Development Tools** (`--profile dev`):
- **rebeldot_adminer** - Database admin UI on port 8080
- **rebeldot_flower** - Celery task monitor on port 5555

**Networking:**
- All services connected via `app_network` bridge network
- Services communicate using DNS names (`postgres`, `redis`, `app`)
- Persistent volumes for data (`postgres_data`, `redis_data`)

**Features:**
- Auto-restart policies (`unless-stopped`)
- Health checks on all core services
- Environment-based configuration via `.env`
- Background task processing with Celery
- Real-time task monitoring with Flower

### Docker Management Commands

```bash
# Start all production services (app, postgres, redis, celery)
docker-compose up -d

# Start with dev tools (+ Adminer on :8080, Flower on :5555)
docker-compose --profile dev up -d

# View logs
docker-compose logs -f app
docker-compose logs -f celery_worker
docker-compose logs -f postgres
docker-compose logs -f redis

# Restart specific service
docker-compose restart app
docker-compose restart celery_worker

# Stop services (keeps volumes)
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Rebuild and restart
docker-compose up --build -d
```

### Docker Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U postgres
```

### Troubleshooting Docker Issues

**Services won't start:**
```bash
docker-compose logs
```

**Database connection failed:**
```bash
docker-compose exec postgres pg_isready -U postgres
```

**Port conflicts:**
```bash
lsof -i :8000
lsof -i :5432
```

**Reset everything:**
```bash
docker-compose down -v
docker system prune -f
docker-compose up --build -d
```