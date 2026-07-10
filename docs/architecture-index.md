# Architecture Index

This index maps every architecture documentation asset to its location and purpose.

## Core Architecture

| Document | Location | Purpose |
|----------|----------|---------|
| System Architecture | [`/docs/System-Architecture.md`](../System-Architecture.md) | Component diagram, ADRs, wiring, deployment modes |
| Component Design | [`/docs/Component-Design.md`](../Component-Design.md) | All 10 components with sub-components and interfaces |
| Data Flow | [`/docs/Data-Flow.md`](../Data-Flow.md) | Query, ingestion, and learning flows |
| API Design | [`/docs/API-Design.md`](../API-Design.md) | Public REST + internal KE API contracts |
| Deployment Architecture | [`/docs/Deployment-Architecture.md`](../Deployment-Architecture.md) | 5 deployment modes, K8s, cost model |

## Domain Specifications

| Document | Location | Purpose |
|----------|----------|---------|
| API Specification | [`/docs/specifications/API-Specification.md`](../specifications/API-Specification.md) | OpenAPI contracts, error catalog (ERR-001 to ERR-018) |
| Database Specification | [`/docs/specifications/Database-Specification.md`](../specifications/Database-Specification.md) | All 9 stores, 14 table schemas, indexes, partitions, RLS |
| Frontend Specification | [`/docs/specifications/Frontend-Specification.md`](../specifications/Frontend-Specification.md) | Component tree, Zustand stores, design tokens |
| Knowledge Engine Specification | [`/docs/specifications/KnowledgeEngine-Specification.md`](../specifications/KnowledgeEngine-Specification.md) | 9 store interfaces, capacity planning, state machine |
| Planner Specification | [`/docs/specifications/Planner-Specification.md`](../specifications/Planner-Specification.md) | Input/output contracts, 7 validation codes |
| Retriever Specification | [`/docs/specifications/Retriever-Specification.md`](../specifications/Retriever-Specification.md) | Retrieval pipeline, scoring weights, caching strategy |
| Security Specification | [`/docs/specifications/Security-Specification.md`](../specifications/Security-Specification.md) | STRIDE, prompt injection, SQL injection, RBAC, RLS |
| Observability Specification | [`/docs/specifications/Observability-Specification.md`](../specifications/Observability-Specification.md) | Metrics, logs, traces, 13 dashboards, 11 alert rules |

## Pipeline & Orchestration

| Document | Location | Purpose |
|----------|----------|---------|
| Workflow Orchestrator Specification | [`/docs/specifications/Workflow-Orchestrator-Specification.md`](../specifications/Workflow-Orchestrator-Specification.md) | Pipeline orchestration, state management, SSE |
| Sequence Diagrams | [`/docs/specifications/Sequence-Diagrams.md`](../specifications/Sequence-Diagrams.md) | 5 complete sequence diagrams |
| State Machines | [`/docs/specifications/State-Machines.md`](../specifications/State-Machines.md) | 7 state machines |

## Engineering Standards

| Document | Location | Purpose |
|----------|----------|---------|
| Engineering Standards | [`/docs/specifications/Engineering-Standards.md`](../specifications/Engineering-Standards.md) | Coding standards, review process, conventions |
| Performance Budgets | [`/docs/specifications/Performance-Budgets.md`](../specifications/Performance-Budgets.md) | Per-component P50/P95/P99 targets |
| Cost Budgets | [`/docs/specifications/Cost-Budgets.md`](../specifications/Cost-Budgets.md) | Per-query cost model, infra cost per tenant |

## Planning

| Document | Location | Purpose |
|----------|----------|---------|
| Implementation Plan | [`/docs/Implementation-Plan.md`](../Implementation-Plan.md) | Master blueprint with parallelism model |
| Architecture Review | [`/docs/Architecture-Review.md`](../Architecture-Review.md) | 12-section review, readiness verdict |
| Status Dashboard | [`/docs/progress/status-dashboard.md`](../progress/status-dashboard.md) | Phase 3/3.5 progress tracking |

## Domain Knowledge

| Document | Location | Purpose |
|----------|----------|---------|
| Knowledge Engine | [`/docs/Knowledge-Engine.md`](../Knowledge-Engine.md) | 9 knowledge stores, KE API, data model |
| Market Analysis | [`/docs/Market-Analysis.md`](../Market-Analysis.md) | Market research and competitive landscape |
| Technology Recommendations | [`/docs/Technology-Recommendations.md`](../Technology-Recommendations.md) | Technology stack rationale |
| Research Summary | [`/docs/Research-Summary.md`](../Research-Summary.md) | Research findings summary |

## Development

| Document | Location | Purpose |
|----------|----------|---------|
| Development Guide | [`/docs/development-guide.md`](../development-guide.md) | Local setup and development workflow |
| Troubleshooting Guide | [`/docs/troubleshooting.md`](../troubleshooting.md) | Common issues and solutions |
| Contributing Guide | [`/docs/contributing.md`](../contributing.md) | Contribution workflow and conventions |
