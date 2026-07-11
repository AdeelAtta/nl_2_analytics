# EP-016: CI/CD & Observability

Epic ID: **EP-016** | Priority: **P0** | Dependencies: **EP-001** | Complexity: **Medium** | Agent: **Infrastructure Agent**

---

Implement CI/CD pipelines and observability infrastructure — automated testing, building, deployment, monitoring, logging, and alerting for the entire platform.

## Goals
- GitHub Actions CI pipeline (lint, typecheck, test, build)
- GitHub Actions CD pipeline (build -> push -> deploy)
- Docker image registry (GHCR or ECR)
- Monitoring stack (Prometheus + Grafana)
- Logging (structured JSON logs, Loki or ELK)
- Health check endpoints for all services
- Sentry for error tracking
- Status page / health aggregator

## Out of Scope
- Production deployment (Phase 4)
- Multi-region setup
- Incident management runbooks

## Tasks

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-135 | Create GitHub Actions CI workflow | P0 | EP-001 | L | ✅ done (6 jobs: lint, typecheck, test, build, security, coverage) |
| TASK-136 | Create GitHub Actions CD workflow | P1 | EP-015 | L | ✅ done (build + push to GHCR + deploy to K8s) |
| TASK-137 | Configure Docker image registry | P0 | TASK-135 | M | ✅ done (GHCR configured in CD workflow) |
| TASK-138 | Add health check endpoints to all services | P0 | EP-001 | M | ✅ done (live, ready, version on port 8100) |
| TASK-139 | Set up Prometheus + Grafana stack | P1 | EP-015 | L | ✅ done (docker-compose with prometheus + grafana + loki) |
| TASK-140 | Implement structured JSON logging | P0 | EP-001 | M | ✅ done (structlog with ISO timestamps + JSON output) |
| TASK-141 | Configure Loki log aggregation | P2 | TASK-140 | M | ✅ done (loki config + docker-compose service + Grafana datasource) |
| TASK-142 | Integrate Sentry for error tracking | P0 | EP-001 | M | ✅ done (sentry_sdk init in app factory, config via SENTRY_DSN) |
| TASK-143 | Create Grafana dashboards | P1 | TASK-139 | L | ✅ done (overview dashboard with request rate, error rate, latency, memory, health) |
| TASK-144 | Configure alerting rules | P1 | TASK-139 | M | ✅ done (4 alert rules: error rate, high latency, service down, memory) |

## Acceptance Criteria
- CI pipeline runs on every push/PR: lint -> typecheck -> unit tests -> integration tests -> build
- CD pipeline deploys to dev on main branch push
- Docker images pushed to registry on every merge
- Health check endpoints return service status
- Prometheus scrapes metrics from all services
- Grafana dashboards show key metrics (requests, latency, errors, saturation)
- Structured logs emitted in JSON format
- Sentry captures and groups errors with context
- Alerting fires on P95 latency > 5s, error rate > 5%, service down

## Definition of Done
- CI green on initial merge
- CD deploys to dev cluster
- Grafana dashboards visible with data
- Sentry test error captured successfully
