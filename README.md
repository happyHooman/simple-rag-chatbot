# Test Assignment

A FastAPI application with comprehensive health monitoring and FAQ question-answering capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Docker & Docker Compose
- `uv` package manager

### Installation
```bash
# Install dependencies (production)
uv sync

# Install with dev dependencies
uv sync --extra dev

# Start database
docker compose up -d

# Start application
uv run python main.py
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
uv run ruff check src/

# Format code
uv run ruff format src/

# Type checking
uv run mypy src/
```

### Database
```bash
# Start database
docker compose up -d

# Stop database
docker compose down
```

## 🏥 Health Monitoring

The application provides comprehensive health monitoring:

- **GET /health** - Overall system status
- **GET /docs** - API documentation
- **POST /ask-question** - FAQ question answering
- **POST /generate-embeddings** - Generate OpenAI embeddings

## 🧪 Testing

### Prebuild Checks
```bash
uv run python scripts/prebuild.py
```

This runs:
- Code linting (Ruff)
- Type checking (MyPy)
- Sanity tests (System readiness)

### Test Categories
- **Sanity tests** - System readiness before deployment
- **Unit tests** - Individual component testing
- **Integration tests** - API endpoint testing

## 🏗️ Project Structure

```
├── src/                    # Application source code
│   ├── config.py          # Configuration settings
│   ├── health_check.py    # Health monitoring
│   ├── embeddings.py      # OpenAI embeddings
│   └── ...
├── tests/                 # Test suites
│   ├── sanity/           # Prebuild sanity tests
│   ├── test_api.py       # API integration tests
│   └── test_health.py    # Health check tests
├── scripts/              # Utility scripts
│   └── prebuild.py       # Prebuild validation
└── docker-compose.yml    # Database setup
```

## 🔧 Configuration

Environment variables (see `.env.example`):
- `API_TITLE`, `API_VERSION`, `API_DESCRIPTION`
- `HOST`, `PORT`, `LOG_LEVEL`
- `DATABASE_URL`, `OPENAI_API_KEY`
- `SIMILARITY_THRESHOLD` - Similarity threshold (default: 0.5)
- `OPENAI_CHAT_MODEL` - Chat model (default: gpt-4o-mini)
- `OPENAI_CHAT_TEMPERATURE` - Model temperature (default: 0.7)

## 📊 Health Status

The `/health` endpoint provides real-time status:
- **operational** - All services running
- **degraded** - Some services unavailable
- **running/stopped** - Container status
- **connected/disconnected** - Database status

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

**Core Services:**
- **FastAPI App** - Port 8000 (configurable via `APP_PORT`)
- **PostgreSQL + pgvector** - Port 5432 (configurable via `POSTGRES_PORT`)

**Development Tools** (run with `--profile dev`):
- **Adminer** - Database admin interface on port 8080

**Networking:**
- All services connected via `app_network` bridge network
- Services use DNS names (e.g., `postgres`, `app`)
- No hardcoded container names for better scalability

**Features:**
- Auto-restart policies (`unless-stopped`)
- Health checks on all core services
- Environment-based configuration via `.env`
- Ready to add more services

### Docker Management Commands

```bash
# Start services (production mode)
docker-compose up -d

# Start with dev tools (Adminer on :8080)
docker-compose --profile dev up -d

# View logs
docker-compose logs -f app
docker-compose logs -f postgres

# Restart specific service
docker-compose restart app

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