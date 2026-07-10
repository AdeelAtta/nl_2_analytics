# TASK-135: Create GitHub Actions CI Workflow

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-135 |
| **Epic** | EP-016 |
| **Priority** | P0 |
| **Complexity** | L |
| **Dependencies** | EP-001, TASK-002, TASK-003 |
| **Agent Owner** | Infrastructure Agent |
| **Status** | backlog |

---

## Description

Create the GitHub Actions CI workflow that runs on every push and pull request to ensure code quality.

## Inputs

- EP-016 epic definition
- Tooling from TASK-002 (Python) and TASK-003 (Node.js)

## Implementation

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Lint
        run: ruff check .
      - name: Type check
        run: mypy --strict .

  test-backend:
    needs: lint-backend
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_DB: test, POSTGRES_PASSWORD: test }
      qdrant:
        image: qdrant/qdrant:v1.12
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Install dependencies
        run: pip install uv && uv sync
      - name: Run tests
        run: pytest --cov --cov-report=term-missing

  lint-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - name: Install dependencies
        run: npm ci
        working-directory: frontend
      - name: Lint
        run: npm run lint
        working-directory: frontend

  build:
    needs: [test-backend, lint-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: docker compose build
```

## Outputs

- `.github/workflows/ci.yml`

## Acceptance Criteria

- [ ] Workflow triggers on push and PR to main
- [ ] Lint backend job runs ruff + mypy
- [ ] Test backend job runs pytest with coverage
- [ ] Lint frontend job runs ESLint
- [ ] Build job builds Docker images
- [ ] PostgreSQL and Qdrant service containers start correctly
- [ ] Workflow completes within 15 minutes

## Definition of Done

- CI workflow runs successfully on test repository
- All jobs execute in correct order (dependencies respected)
- Task status updated to `done`
