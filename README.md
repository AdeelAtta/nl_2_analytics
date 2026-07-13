# SchemaIntern — DB-Aware NL to SQL

Schema-aware natural language to SQL — knows your database schema and generates accurate, safe SQL queries.

## Live Demo

| Service | URL | Stack |
|---|---|---|
| **Frontend** | [nl-2-analytics.vercel.app](https://nl-2-analytics.vercel.app) | Next.js 15 on Vercel (free) |
| **Backend API** | [schemaintern-backend.onrender.com](https://schemaintern-backend.onrender.com) | FastAPI on Render (free) |
| **Database** | Render PostgreSQL (managed) | PostgreSQL 16 (free) |

Register an account, connect your database, and start querying in natural language.

## Architecture

SchemaIntern connects to enterprise databases (PostgreSQL, MySQL, Snowflake, BigQuery) and lets users ask questions in natural language. The platform:

1. **Discovers** schema meaning automatically (no manual YAML)
2. **Retrieves** relevant context from a self-learning Knowledge Engine
3. **Plans** optimal query strategies
4. **Generates** and validates SQL
5. **Enforces** enterprise security policies
6. **Executes** queries safely
7. **Learns** from feedback

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Frontend | Next.js 15, TypeScript, Tailwind, shadcn/ui |
| Database | PostgreSQL 16 |
| AI | LangGraph, vLLM/SGLang, SQLCoder |
| Infrastructure | Docker |
| CI/CD | GitHub Actions |
| Observability | OpenTelemetry, Prometheus, Grafana |

## Quick Start

### Option A: Dev Stack (recommended)

Starts everything with hot-reload — PostgreSQL, backend, and frontend.

```bash
docker compose -f docker-compose.dev.yml up --build
```

Set your HuggingFace token for AI-generated table/column descriptions:

```env
# Get a free token: https://huggingface.co/settings/tokens
HF_TOKEN=hf_your_token_here
```

| Service | URL | Default Credentials |
|---|---|---|
| Frontend | `http://localhost:3000` | — |
| API | `http://localhost:8100` | — |
| PostgreSQL | `localhost:5432` | `postgres` / `postgres` (8 test databases auto-seeded) |

Stop with `docker compose -f docker-compose.dev.yml down`.

### Option B: Production Stack

Starts with nginx reverse proxy — single port, no hot-reload.

```bash
cp .env.prod.example .env.prod
# Edit .env.prod with strong secrets (POSTGRES_PASSWORD, JWT_SECRET)
docker compose up --build
```

| Service | URL | Notes |
|---|---|---|
| App | `http://localhost:8080` | Single entry point |
| PostgreSQL | Internal (Docker) | No test databases in production |

Migrations run automatically on startup.

### Option C: Native (manual)

#### Prerequisites

- Python 3.12+, Node.js 20+, Docker
- uv: `pip install uv`

```bash
make install
cp .env.example .env
docker compose -f infra/docker/docker-compose.db.yml up -d
make db-migrate
make dev
```

| Service | URL |
|---|---|
| Frontend | `http://localhost:3000` |
| API | `http://localhost:8100` |

### Test Databases

On first start, all 8 test databases are auto-seeded into PostgreSQL:

| Database | Description | Tables |
|---|---|---|
| `chinook` | Music store | Artist, Album, Track, Customer, Invoice, Employee, Genre, Playlist, MediaType, InvoiceLine, PlaylistTrack |
| `titanic` | Passenger survival data | passenger |
| `dvdrental` | DVD rental store | actor, film, customer, rental, payment, category, language, inventory, staff, store |
| `lego` | Lego sets and parts | sets, themes, parts, colors, inventories, part_categories |
| `netflix` | Netflix titles | titles, cast, genres, directors, countries |
| `pagila` | DVD rental (PostgreSQL port) | Same structure as dvdrental |
| `periodic_table` | Chemical elements | elements, types |
| `happiness_index` | World happiness report | happiness, regions, year |

### Quick Demo (Docker only)

Use the **"Try Chinook Demo"** button on the **Settings → Connections** page to auto-fill and sync.

### Manual Connection

Go to **Settings → Connections** and enter:

| Field | Docker (dev stack) | Native (local) |
|---|---|---|
| Host | `postgres` | `localhost` |
| Port | `5432` | `5432` |
| Database | `chinook` (or any above) | same |
| Username | `postgres` | `postgres` |
| Password | `postgres` | `postgres` |

Click **Test Connection**, then **Sync Schema**. Once synced, the database appears in the dropdown on the **Query** and **Schema** pages.

Try queries: `"how many male passengers?"`, `"list all Rock tracks"`, `"total sales by country"`.

> **Docker tip**: Use `postgres` as the host (Docker service name) — it resolves to the PostgreSQL container via Docker's internal DNS.

### Environment Files

| File | Used by | Purpose |
|---|---|---|
| `.env.dev` | `docker-compose.dev.yml` | Dev defaults (tracked in git) |
| `.env.prod` | `docker-compose.yml` | Production secrets (not tracked) |
| `.env.example` | — | Template with all variables documented |

## Workflow Commands

| Command | Description |
|---|---|
| `make install` | Install all dependencies (backend + frontend) |
| `make dev` | Start native dev servers (backend :8100, frontend :3000) |
| `make test` | Run all tests |
| `make test-backend` | Run backend tests only |
| `make test-frontend` | Run frontend tests only |
| `make lint` | Run all linters |
| `make typecheck` | Run type checkers (mypy + tsc) |
| `make format` | Format all code |
| `make build-backend` | Build backend Docker image |
| `make build-frontend` | Build frontend Docker image |
| `make prod` | Start production stack |
| `make prod-logs` | Tail production logs |
| `make prod-down` | Stop production stack |
| `make dev-up` | Start dev stack (`docker compose -f docker-compose.dev.yml up -d --build`) |
| `make dev-down` | Stop dev stack |
| `make db-migrate` | Run database migrations |
| `make db-seed` | Seed placeholder data (legacy) |
| `make seed DB=lego PASSWORD=123` | Seed a test database |
| `make seed-all PASSWORD=123` | Seed all test databases |
| `make seed-docker DB=chinook` | Seed using Docker PostgreSQL |
| `make clean` | Clean build artifacts |

### Docker

| Command | Description |
|---|---|
| `docker compose -f docker-compose.dev.yml up --build` | Start dev stack (hot-reload) |
| `docker compose -f docker-compose.dev.yml up --build -d` | Dev stack in background |
| `docker compose -f docker-compose.dev.yml down` | Stop dev stack |
| `docker compose -f docker-compose.dev.yml logs -f backend` | Tail backend logs |
| `docker compose up --build` | Start production stack (nginx proxy) |
| `docker compose down` | Stop production stack |
| `docker compose -f infra/docker/docker-compose.db.yml up -d` | Start only PostgreSQL + PgBouncer |

### Production Stack

```bash
# 1. Create env file with strong secrets
cp .env.prod.example .env.prod
# Edit .env.prod — set POSTGRES_PASSWORD and JWT_SECRET

# 2. Start
docker compose up -d --build

# 3. Access
open http://localhost:8080
```

| Service | Internal | Exposed |
|---|---|---|
| `nginx` | 80 | **8080** |
| `backend` | 8100 | — |
| `frontend` | 3000 | — |
| `postgres` | 5432 | — |

### Manual seeds (without Make)

```bash
# List available databases
./bin/seed.sh

# Seed one database
POSTGRES_PASSWORD=123 ./bin/seed.sh lego

# Seed all databases
POSTGRES_PASSWORD=123 ./bin/seed.sh --all

# Target Docker PostgreSQL
./bin/seed.sh --docker lego
```

## Project Structure

```
schemaintern/
├── backend/               # Python FastAPI backend
│   ├── app/               # External API (port 8100) — auth, query, schema
│   ├── ke/                # Knowledge Engine API (port 8200)
│   ├── schema_intelligence/  # Schema discovery & annotation
│   ├── shared/            # Shared Pydantic models
│   ├── alembic/           # DB migrations
│   ├── scripts/           # Utility scripts
│   ├── tests/             # Backend tests
│   └── data/              # File-based storage (users, tenants)
├── frontend/              # Next.js application (port 3000)
├── infra/                 # Infrastructure
│   ├── docker/            # Dockerfiles and Compose
│   ├── grafana/           # Grafana dashboards
│   └── scripts/           # Utility scripts
├── tests/                 # Root integration/unit tests
├── docs/                  # Documentation
└── test-databases/        # SQL seed data
```

## Development

See [Development Guide](docs/development-guide.md) for detailed setup instructions.

## Documentation

All documentation is in `/docs/`. Key documents:

- [Architecture Overview](docs/System-Architecture.md)
- [API Specification](docs/specifications/API-Specification.md)
- [Database Specification](docs/specifications/Database-Specification.md)
- [Engineering Standards](docs/specifications/Engineering-Standards.md)
- [Implementation Plan](docs/Implementation-Plan.md)

## Contributing

See [Contributing Guide](docs/contributing.md)

## License

Proprietary — All Rights Reserved
