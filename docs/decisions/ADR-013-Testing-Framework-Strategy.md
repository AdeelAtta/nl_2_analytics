# ADR-013: Testing Framework Strategy

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-013 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

The platform spans Python backend (FastAPI, LangGraph agents, KE API), TypeScript frontend (React 19, Next.js), and infrastructure (Docker, K8s, Terraform). A testing strategy must cover unit, integration, end-to-end, performance, and infrastructure testing across all layers. The strategy must integrate with CI/CD, provide fast feedback, and scale from 10 to 100+ engineers.

## Decision

Use the following testing framework per layer:

| Layer | Framework | Scope |
|-------|-----------|-------|
| Python unit/integration | pytest 8+ (pytest-asyncio, pytest-cov) | Backend services, agents, KE API |
| Python property-based | hypothesis | Schema validation, edge case discovery |
| TypeScript unit | vitest | React components, Zustand stores, utils |
| E2E integration | Playwright | Full user workflows, multi-service scenarios |
| Performance | k6 | API load tests, GPU inference benchmarks |
| Infrastructure | terratest | Terraform module validation |
| Contract | openapi-to-pytest + zod | API request/response validation |

## Rationale

- **pytest** is the Python standard with the richest plugin ecosystem (asyncio, cov, xdist for parallel execution)
- **vitest** is faster than Jest (native ESM, esbuild transform), integrates natively with Vite/Next.js toolchain
- **Playwright** supports multi-browser + mobile + API testing in a single framework, is faster in CI than Cypress, and has native TypeScript support
- **k6** is the only performance testing tool with native Go runtime (low overhead), JavaScript scripting, and CI integration
- **hypothesis** finds edge cases that manual tests miss — critical for schema parsing and SQL generation
- **terratest** validates Terraform modules before deployment (prevent infrastructure drift)

## Consequences

### Positive
- Single testing framework per language layer — no fragmentation
- Fast CI feedback (pytest-xdist parallel, vitest native ESM, Playwright sharding)
- Property-based testing catches edge cases in schema/SQL parsing
- Performance tests run in CI (k6 exits with non-zero on SLA breach)
- Contract tests catch API breaking changes before deployment

### Negative
- Two test frameworks to maintain (Python + TypeScript) vs single-language stack
- Playwright E2E tests are slower and more flaky than unit tests
- k6 requires JavaScript/TypeScript scripting knowledge (Python team may struggle)
- Additional CI minutes for performance and E2E test suites
- Contract tests add maintenance overhead when API contracts change

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| unittest (Python) | Less flexible than pytest; no built-in async support; verbose assertions |
| Jest (TypeScript) | Heavier than vitest; slower transform; not native ESM |
| Cypress (E2E) | Slower CI execution; no mobile support; worse API testing |
| Locust (performance) | Python-based but less CI-friendly; no built-in SLA assertions |
| Manual testing only | Not scalable beyond MVP; regression risk |
| Single E2E-only strategy | Feedback loop too slow; no unit-level coverage |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Flaky Playwright tests degrading CI trust | Medium | High | Retry flaky tests (max 3); quarantine consistently flaky tests |
| Performance test environment not matching prod | Medium | Medium | Dedicated perf environment with same GPU/K8s spec ratios |
| Test data pollution across parallel runs | Medium | High | Database-per-test-fixture; rollback after each suite |
| Low coverage of agent orchestration paths | Medium | High | Integration tests for each LangGraph state transition |
| Contract test maintenance burden with rapid API changes | High | Medium | Auto-generate contract tests from OpenAPI spec; regenerate on spec change |

## Trade-offs

- **pytest-asyncio complexity**: Python async tests require pytest-asyncio markers and event loop management — adds boilerplate but is required for FastAPI/httpx testing
- **E2E coverage vs speed**: Playwright tests provide highest confidence but slowest feedback. Strategy: critical user journeys only as E2E; all other logic tested at unit/integration level
- **Performance test accuracy**: k6 results in CI use synthetic data and limited GPU — accurate for relative regression detection but not absolute capacity planning
- **Static vs dynamic analysis**: Testing catches runtime errors only; static analysis (mypy, pyright, ESLint) catches code-quality issues earlier in the pipeline

## Related ADRs

- ADR-011: Technology Stack Selection (Python/TypeScript ecosystem)
- ADR-014: CI/CD and GitOps Strategy (pipeline integration, quality gates)

## References

- [Engineering-Standards.md](../specifications/Engineering-Standards.md) §3 (Testing Standards)
- [Implementation-Plan.md](../Implementation-Plan.md) §6 (Quality Gates)
