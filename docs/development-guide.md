# Development Guide

## Prerequisites

- **Python 3.12+** — Runtime for backend services
- **Node.js 20+** — Runtime for frontend application
- **Docker & Docker Compose** — Infrastructure services (PostgreSQL, Redis, Qdrant)
- **uv** — Python package manager (`pip install uv`)
- **pnpm** — Preferred Node.js package manager (`npm install -g pnpm`)

## Setup

### 1. Clone the Repository

```bash
git clone <repo-url>
cd openquery
```

### 2. Install Dependencies

```bash
make install
```

This runs:
- `uv sync` in `backend/` — installs Python dependencies
- `npm install` in `frontend/` — installs Node.js dependencies

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` to match your local setup. Defaults work for local development.

### 4. Start Infrastructure Services

```bash
docker compose -f infra/docker/docker-compose.yml up -d postgres redis qdrant
```

### 5. Run Database Migrations

```bash
make db-migrate
```

### 6. Seed Development Data (Optional)

```bash
make db-seed
```

## Running Locally

### Backend

```bash
make dev
```

Starts uvicorn on port 8100 with hot reload. Alternatively:

```bash
cd backend && uv run uvicorn app.main:create_app --reload --port 8100
```

### Frontend

```bash
cd frontend && npm run dev
```

Starts Next.js dev server on port 3000.

### All Services

```bash
# Start everything
docker compose -f infra/docker/docker-compose.yml up -d
make dev               # backend + frontend

# Stop everything
make down
```

## Testing

### Unit Tests

```bash
make test-backend     # Backend unit tests (pytest)
make test-frontend    # Frontend unit tests (Vitest/Jest)
```

### Integration Tests

```bash
cd backend && uv run pytest tests/integration
```

### End-to-End Tests

```bash
# Requires all services running
cd frontend && npm run test:e2e
```

### Load Tests

```bash
cd backend && uv run pytest tests/load
```

## Code Style

### Python (Backend)

| Tool | Command | Configuration |
|------|---------|---------------|
| Ruff (linter) | `uv run ruff check .` | `backend/pyproject.toml` |
| Ruff (formatter) | `uv run ruff format .` | `backend/pyproject.toml` |
| Mypy (type checker) | `uv run mypy .` | `backend/pyproject.toml` |

### TypeScript/JavaScript (Frontend)

| Tool | Command | Configuration |
|------|---------|---------------|
| ESLint | `npm run lint` | `frontend/eslint.config.js` |
| Prettier | `npx prettier --write .` | `frontend/.prettierrc` |
| TypeScript | `npm run typecheck` | `frontend/tsconfig.json` |

### Quick Format

```bash
make format    # Formats both backend and frontend
make lint      # Lints both backend and frontend
make typecheck # Type checks both backend and frontend
```

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to enforce code quality.

```bash
# Run on all files
make pre-commit

# Run hooks on staged files (automatic on git commit)
```

Hooks configured:
- `ruff` — Python linting and formatting
- `mypy` — Python type checking
- `eslint` — TypeScript/JavaScript linting
- `prettier` — Code formatting
- `trailing-whitespace` — Removes trailing whitespace
- `end-of-file-fixer` — Ensures files end with newline

## Conventional Commits

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

### Types

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Maintenance, tooling, config |
| `docs` | Documentation |
| `refactor` | Code restructuring |
| `test` | Adding or updating tests |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |
| `style` | Formatting, linting |

### Examples

```
feat(ke): add schema store vector search
fix(query-pipeline): handle empty result sets
docs: update development guide
chore(deps): upgrade fastapi to 0.115.0
```

## Debugging

### Backend

- **Enable debug logging**: Set `LOG_LEVEL=DEBUG` in `.env`
- **OpenAPI docs**: Visit `http://localhost:8100/docs`
- **ReDoc**: Visit `http://localhost:8100/redoc`

### Frontend

- **React DevTools**: Install browser extension
- **API calls**: Check browser Network tab
- **Next.js debug**: Set `NEXT_PUBLIC_DEBUG=true`

### Databases

- **PostgreSQL**: `psql -h localhost -U openquery -d openquery`
- **Redis**: `redis-cli -h localhost -p 6379`
- **Qdrant**: REST API at `http://localhost:6333/dashboard`

### Observability

- **Grafana**: `http://localhost:3001` (admin/admin)
- **Prometheus**: `http://localhost:9090`
- **Tempo (traces)**: `http://localhost:3200`

## Common Issues & Troubleshooting

See the [Troubleshooting Guide](docs/troubleshooting.md) for solutions to common problems.

## Project Structure

```
openquery/
├── backend/            # Python FastAPI services
│   ├── public-api/     # External API (port 8100)
│   ├── ke-api/         # Knowledge Engine API (port 8200, internal)
│   ├── query-pipeline/ # NL2SQL agent pipeline
│   ├── schema-intel/   # Schema intelligence workers
│   ├── learning-loop/  # Self-learning workers
│   ├── auth/           # Authentication service
│   └── lib/            # Shared Python libraries
├── frontend/           # Next.js application
├── infra/              # Infrastructure
│   ├── docker/         # Dockerfiles and Compose
│   ├── k8s/            # Kubernetes manifests
│   ├── terraform/      # Terraform modules
│   └── helm/           # Helm charts
├── shared/             # Shared type definitions
└── docs/               # Documentation
```
