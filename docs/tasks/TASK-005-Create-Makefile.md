# TASK-005: Create Makefile with Common Commands

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-005 |
| **Epic** | EP-001 |
| **Priority** | P1 |
| **Complexity** | S |
| **Dependencies** | TASK-001, TASK-002 |
| **Agent Owner** | Infrastructure Agent |
| **Status** | backlog |

---

## Description

Create a Makefile at the repository root with common development commands for both backend and frontend.

## Inputs

- Monorepo structure from TASK-001
- Python tooling from TASK-002 (uv, pytest, ruff, mypy)
- Node.js tooling from TASK-003

## Implementation

Targets to implement:

```
.PHONY: install dev test lint typecheck build clean help

install:           # Install all dependencies (backend + frontend)
dev:               # Start all services in dev mode
test:              # Run all tests (unit + integration)
lint:              # Run ruff linter on all Python files
typecheck:         # Run mypy type checker on all Python files
build:             # Build all Docker images
clean:             # Clean all build artifacts
help:              # Show available targets
```

Backend install: `uv sync`
Frontend install: `npm install`
Backend test: `pytest`
Backend lint: `ruff check .`
Backend typecheck: `mypy --strict`

## Outputs

- **Files to create**: `Makefile` at root
- **Files to modify**: None

## Acceptance Criteria

- [ ] `make help` lists all targets with descriptions
- [ ] `make install` completes successfully
- [ ] `make test` runs pytest
- [ ] `make lint` runs ruff
- [ ] `make typecheck` runs mypy

## Definition of Done

- All targets execute without errors on a clean checkout
- Task status updated to `done`
