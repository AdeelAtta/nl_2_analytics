# ADR-007: LangGraph for Agent Orchestration

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-007 |
| **Date** | 2026-07-10 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

The NL2SQL pipeline requires multi-agent orchestration with sequential processing, conditional branching, and repair/reflection cycles. The orchestration framework must support DAG execution, cyclic graphs (for the repair loop), and shared state across agents.

## Decision

Use LangGraph for multi-agent pipeline orchestration.

## Rationale

LangGraph provides DAG + cycles + conditional branching, which maps directly to our NL2SQL pipeline (sequential agents with conditional repair/reflection loops). It has the most mature production ecosystem for Python-based multi-agent systems. Built-in state management for agent context eliminates the need for a custom state machine.

## Consequences

### Positive
- DAG + cycle support matches NL2SQL pipeline requirements exactly
- Built-in state management for agent context
- Largest production ecosystem for Python-based multi-agent systems
- Active development and community support

### Negative
- Dependency on LangGraph API stability
- Team learning curve for LangGraph-specific concepts
- Version lock-in risk (LangGraph changes may require migration)
- Relatively young project — breaking changes possible

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Custom orchestration | Higher development cost; no built-in state management, cycles, or branching |
| CrewAI | Less mature, fewer production deployments |
| AutoGen | Microsoft-centric, Python-only, less flexible graph model |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LangGraph API breaking changes during development cycle | Medium | High | Pin LangGraph version; API surface tests; upgrade only in dedicated refactor sprints |
| LangGraph runtime performance degrades with deep agent graphs | Medium | Medium | Profile agent graph execution in CI; optimize state serialization (reduce shared state size); consider multi-threaded node execution |
| Team learning curve slows initial agent development velocity | High | Medium | Dedicated LangGraph spike (2 days) before agent implementation; pair programming for first agent; internal documentation of patterns |
| LangGraph becomes abandoned or deprioritized by maintainers | Low | High | No immediate migration needed; framework abstraction allows swapping runtime with custom implementation if required |
| Cyclic agent loops (repair/reflection) do not terminate | Medium | High | Max iteration limit (2 cycles); monotonic improvement check (exit if not improving); timeout per agent graph execution |

## Trade-offs

- **LangGraph vs custom orchestration**: LangGraph provides state management, DAG+cycle execution, and conditional branching out of the box — saving 4-6 weeks of custom development. The trade-off is dependency on LangGraph's API stability and release cadence. Custom orchestration would eliminate external dependency but increase development time and risk of design errors
- **LangGraph vs CrewAI/AutoGen**: LangGraph is chosen over CrewAI (less mature, fewer production deployments) and AutoGen (Microsoft-centric, less flexible graph model). LangGraph's explicit graph model maps most directly to our NL2SQL pipeline with repair/reflection cycles
- **Shared state via LangGraph vs per-node isolated state**: LangGraph's shared state (passed between nodes) enables the repair agent to see the initial SQL, error, and reflection context in one state object. Per-node isolated state would require explicit context passing but reduce state serialization overhead. Shared state chosen for development simplicity

## Related ADRs

- ADR-001: Knowledge Engine as Architectural Core (agents consume KE API via LangGraph)
- ADR-003: Components Are Stateless Executors (agent nodes are stateless LangGraph nodes)
- ADR-011: Technology Stack Selection (Python, LangGraph ecosystem)

## References

- [Architecture-Review.md](../Architecture-Review.md) §10.7
- [AI-Agent-Specification.md](../specifications/AI-Agent-Specification.md) §3 (Agent Architecture), §4 (Agent State Management)
- [Planner-Specification.md](../specifications/Planner-Specification.md) §3 (Pipeline Orchestration)
