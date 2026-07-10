# TASK-126: Create Dockerfiles for All Services

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-126 |
| **Epic** | EP-015 |
| **Priority** | P0 |
| **Complexity** | M |
| **Dependencies** | EP-001 |
| **Agent Owner** | Infrastructure Agent |
| **Status** | backlog |

---

## Description

Create Dockerfiles for all backend services and the frontend. Use multi-stage builds for production optimization.

## Inputs

- Service structures from EP-001
- Technology stack from Implementation-Plan.md §5

## Implementation

Create Dockerfiles in `/infra/docker/`:

**1. Dockerfile.ke** (Knowledge Engine API):
- Base: `python:3.12-slim`
- Install uv, install dependencies, copy source
- Port 8200
- Health check: `/health`
- CMD: `uvicorn backend.ke.api.main:app --host 0.0.0.0 --port 8200`

**2. Dockerfile.schema-intelligence**:
- Same base, different source
- CMD: schema intelligence service entrypoint

**3. Dockerfile.query-pipeline**:
- Same base, different source  
- CMD: query pipeline service entrypoint
- GPU support: `nvidia/cuda:12.4-runtime` variant for GPU inference nodes

**4. Dockerfile.api** (Public API):
- Same base
- Port 8100
- CMD: public API entrypoint

**5. Dockerfile.frontend**:
- Multi-stage: `node:20-alpine` for build, `nginx:alpine` for serve
- Copy `.next/` build output
- Port 3000

## Outputs

- `/infra/docker/Dockerfile.ke`
- `/infra/docker/Dockerfile.schema-intelligence`
- `/infra/docker/Dockerfile.query-pipeline`
- `/infra/docker/Dockerfile.api`
- `/infra/docker/Dockerfile.frontend`

## Acceptance Criteria

- [ ] All Dockerfiles build successfully
- [ ] Multi-stage builds used where appropriate (frontend, GPU)
- [ ] Images are < 500MB (Python) and < 100MB (frontend)
- [ ] Health check endpoints work
- [ ] Used different base images where needed (GPU vs CPU)

## Definition of Done

- `docker build -f infra/docker/Dockerfile.ke .` succeeds
- All images build and are functional
- Task status updated to `done`
