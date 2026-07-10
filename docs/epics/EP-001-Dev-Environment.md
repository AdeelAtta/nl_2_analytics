# EP-001: Development Environment & Monorepo

| Metadata | Value |
|----------|-------|
| **Epic ID** | EP-001 |
| **Priority** | P0 |
| **Dependencies** | None |
| **Complexity** | Medium |
| **Agent Owner** | Infrastructure Agent |
| **Status** | done |

---

## Description

Set up the development environment, monorepo structure, tooling, and local development workflows. Establish the foundation that all other epics build on.

## Goals

- Monorepo with Python backend and JavaScript frontend workspaces
- Consistent local development experience (one command to run all services)
- Pre-commit hooks for linting/formatting/type checking
- Makefile with common commands
- Python package structure with `pyproject.toml` (uv)
- Basic Docker Compose setup with PostgreSQL, Qdrant, Redis

## Out of Scope

- Production Docker/K8s configuration (EP-015, EP-016)
- Application business logic
- CI/CD pipelines

## Tasks

| ID | Task | Priority | Dependencies | Est. | Status |
|----|------|----------|-------------|------|--------|
| TASK-001 | Initialize monorepo with workspace structure | P0 | None | S | done |
| TASK-002 | Configure Python tooling (uv, ruff, mypy, pytest) | P0 | TASK-001 | M | done |
| TASK-003 | Configure Node.js/Next.js tooling | P0 | TASK-001 | M | done |
| TASK-004 | Setup Docker Compose for local services (PG, Qdrant, Redis) | P0 | TASK-001 | M | done |
| TASK-005 | Create Makefile with common commands | P1 | TASK-001 | S | done |
| TASK-006 | Setup pre-commit hooks | P0 | TASK-002 | S | done |
| TASK-007 | Create README.md with setup instructions | P1 | TASK-001 | S | done |
| TASK-008 | Setup Python shared models package | P1 | TASK-002 | M | done |

## Acceptance Criteria

- [ ] `make install` installs all dependencies in under 2 minutes
- [ ] `make dev` starts all services (API, frontend, PG, Qdrant, Redis)
- [ ] `make test` runs all unit tests with coverage
- [ ] `make lint` passes with zero errors
- [ ] `make typecheck` passes with zero errors
- [ ] Pre-commit hooks run ruff + mypy on staged Python files
- [ ] Docker Compose starts PG 16, Qdrant 1.12, Redis 7 in under 30 seconds
- [ ] `pyproject.toml` exports all shared packages correctly
- [ ] Backend and frontend can start in development mode simultaneously

## Definition of Done

- All tasks marked `done`
- A new developer can clone the repo, run `make install && make dev`, and see a running system
- CI pipeline stays green
