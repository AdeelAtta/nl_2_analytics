# EP-015: Multi-Tenant Infrastructure

Epic ID: **EP-015** | Priority: **P0** | Dependencies: **EP-001** | Complexity: **Medium** | Agent: **Infrastructure Agent**

---

Implement the cloud-agnostic Kubernetes infrastructure for the SaaS deployment mode, with multi-tenant isolation, auto-scaling, and cost optimization.

## Goals
- Dockerfiles for all services (KE API, Schema Intel, Query Pipeline, Public API, Frontend)
- K8s manifests for 4 node pools (system, ke, pipeline, frontend)
- Helm charts for reusable deployment
- Terraform modules for cloud-agnostic provisioning
- Multi-tenant isolation via RLS (already covered in EP-002) + resource quotas
- Auto-scaling (HPA based on CPU/memory/custom metrics)
- Ingress configuration (Traefik or nginx-ingress)
- Secret management (HashiCorp Vault or external-secrets)

## Out of Scope
- Production deployment (Phase 4)
- CI/CD pipelines (EP-016)
- Monitoring stack (EP-016)

## Tasks

| ID | Name | P | Deps | Est |
|----|------|---|---|-----|
| TASK-126 | Create Dockerfiles for all services | P0 | EP-001 | L |
| TASK-127 | Create K8s manifests for dev environment | P0 | TASK-126 | XL |
| TASK-128 | Create Helm charts for reusable deployment | P1 | TASK-127 | L |
| TASK-129 | Create Terraform modules (cloud-agnostic) | P0 | TASK-126 | XL |
| TASK-130 | Configure K8s namespaces and network policies | P0 | TASK-127 | M |
| TASK-131 | Implement HPA configurations | P1 | TASK-127 | M |
| TASK-132 | Configure ingress | P0 | TASK-127 | M |
| TASK-133 | Set up secret management | P0 | TASK-127 | M |
| TASK-134 | Write infrastructure tests | P1 | TASK-127 | L |

## Acceptance Criteria
- Docker images build successfully for all services
- K8s manifests deploy all services to minikube/kind
- Namespace isolation works (no cross-namespace access)
- HPA scales pods based on CPU/memory
- Ingress routes requests to correct services
- Secrets managed securely (not in git)
- Terraform modules work with at least 2 cloud providers

## Definition of Done
- Docker Compose (local) + K8s (dev cluster) both run the full stack
- Terraform provisions a working cluster
- All manifests pass `kubeconform` validation
