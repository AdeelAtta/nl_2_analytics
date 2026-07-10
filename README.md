# OpenQuery — Enterprise Data Intelligence Platform

AI-powered natural language querying for enterprise databases.

## Architecture

OpenQuery connects to enterprise databases (PostgreSQL, MySQL, Snowflake, BigQuery) and lets users ask questions in natural language. The platform:

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
| Database | PostgreSQL 16, Redis 7, Qdrant 1.12 |
| AI | LangGraph, vLLM/SGLang, SQLCoder |
| Infrastructure | Docker, K8s, Terraform, Helm |
| CI/CD | GitHub Actions, ArgoCD |
| Observability | OpenTelemetry, Prometheus, Grafana |

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- uv (Python package manager): `pip install uv`
- pnpm (recommended) or npm

### Setup

```bash
# Clone and enter repo
git clone <repo-url> && cd openquery

# Install dependencies
make install

# Set up environment
cp .env.example .env

# Start infrastructure services
docker compose -f infra/docker/docker-compose.yml up -d postgres redis qdrant

# Run database migrations
make db-migrate

# Start development servers
make dev
```

### Verify

```bash
# Backend health
curl http://localhost:8100/api/v1/health/live

# Frontend
open http://localhost:3000

# Grafana dashboards
open http://localhost:3001
```

## Project Structure

```
openquery/
├── backend/            # Python FastAPI services
│   ├── public-api/     # External API (port 8100)
│   ├── ke-api/         # Knowledge Engine API (port 8200)
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

## Development

See [Development Guide](docs/development-guide.md) for detailed setup instructions.

## Documentation

All documentation is in `/docs/`. Key documents:

- [Architecture Overview](docs/System-Architecture.md)
- [API Specification](docs/specifications/API-Specification.md)
- [Database Specification](docs/specifications/Database-Specification.md)
- [Engineering Standards](docs/specifications/Engineering-Standards.md)
- [Implementation Plan](docs/Implementation-Plan.md)

## License

Proprietary — All Rights Reserved
