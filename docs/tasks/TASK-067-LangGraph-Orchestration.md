# TASK-067: Implement LangGraph Agent Orchestration

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-067 |
| **Epic** | EP-009 |
| **Priority** | P0 |
| **Complexity** | XL |
| **Dependencies** | EP-008 |
| **Agent Owner** | Query Pipeline Agent |
| **Status** | backlog |

---

## Description

Implement the LangGraph agent orchestration framework for the 10-agent NL2SQL pipeline. This is the core orchestration layer that manages agent state, transitions, iteration limits, error recovery, and cost tracking.

## Inputs

- Component-Design.md §5.1 (Pipeline orchestration)
- Data-Flow.md §2.1 (Query flow sequence)
- EP-008 Intent + Planning agents

## Implementation

Create `/backend/query-pipeline/generator/orchestrator.py`:

```python
# StateGraph with:
# - QueryState: user_query, context, intent, plan, sql_candidates,
#               selected_sql, policy_results, execution, reflection,
#               errors, cost, metadata
# - Nodes: intent -> retrieval -> planner -> generator ->
#          [validation -> repair (max 2)] -> policy_enforcement ->
#          execution -> reflection
# - Edges:
#   intent -> retrieval (always)
#   retrieval -> planner (always)  
#   planner -> generator (always)
#   generator -> validation (always)
#   validation -> policy_enforcement (if valid) | repair (if invalid)
#   repair -> validation (max 2 cycles)
#   policy_enforcement -> execution (if passed) | END (if rejected)
#   execution -> reflection (always)
#   reflection -> END (always)
#
# Each node:
#   - Is an async function
#   - Receives QueryState
#   - Returns updated QueryState
#   - Logs execution time and cost
#   - Handles errors by setting state.error
```

Key design decisions:
- Max 2 repair-validation cycles
- State serializable for checkpointing
- Cost tracking at each node
- Timeout per node (configurable)

## Outputs

- `/backend/query-pipeline/generator/orchestrator.py`
- `/backend/query-pipeline/generator/__init__.py`

## Acceptance Criteria

- [ ] LangGraph StateGraph correctly defines the 10-agent pipeline (intent → retriever → planner → generator → [validator → repair]² → policy_enforcement → execution → reflection)
- [ ] State transitions follow the expected sequence
- [ ] Max iteration limit (2 cycles) enforced
- [ ] Error in any node is captured and propagated
- [ ] Cost accumulated across all nodes
- [ ] State is serializable (JSON)

## Test Requirements

- Unit tests: graph structure verification
- Unit tests: state transition correctness
- Integration test: full pipeline with mock agents
- Test: iteration limit enforcement
- Test: error propagation

## Definition of Done

- Orchestrator executes the full pipeline with mock agents
- State transitions verified
- Error handling tested
- Task status updated to `done`
