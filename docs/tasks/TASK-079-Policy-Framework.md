# TASK-079: Implement Policy Enforcement Framework

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-079 |
| **Epic** | EP-010 |
| **Priority** | P0 |
| **Complexity** | L |
| **Dependencies** | EP-002 |
| **Agent Owner** | Query Pipeline Agent |
| **Status** | backlog |

---

## Description

Implement the policy enforcement stack framework using a chain-of-responsibility pattern. Each layer is a step in the chain; any layer can reject the query, failing closed. Layers L2-L10 are fully deterministic (no LLM). L1 may use LLM for intent classification but degrades gracefully on timeout.

## Inputs

- Component-Design.md §6 (Policy Enforcement Stack)
- EP-010 epic definition
- AI-Agent-Specification.md §7 (Policy Enforcement Agent)

## Implementation

Create `/backend/query-pipeline/policy/chain.py`:

```python
# Policy Enforcement framework:
# - PolicyLayerBase abstract class with check(query, context) -> PolicyResult
# - PolicyResult: passed (bool), reason (str), metadata (dict), layer_name (str)
# - PolicyChain: ordered list of policy layers
#   - add_layer(layer)
#   - process(query, context) -> list[PolicyResult]
#   - If any layer fails: return immediately with fail-closed
#   - If all pass: return passed=True
#
# Layer contract:
# - Stateless (all state in context)
# - Fast layers first (sanitization, RBAC)
# - Expensive layers last (SQL validation, anomaly detection)
# - Each layer logs its decision
# - L2-L10: no LLM calls, deterministic only

class PolicyResult(BaseModel):
    layer_name: str
    passed: bool
    reason: str = ""
    metadata: dict = {}
    duration_ms: float = 0.0

class PolicyLayerBase(ABC):
    @abstractmethod
    async def check(self, query: str, context: PolicyContext) -> PolicyResult: ...

class PolicyChain:
    def __init__(self):
        self._layers: list[PolicyLayerBase] = []
    
    def add_layer(self, layer: PolicyLayerBase) -> None: ...
    
    async def process(self, query: str, context: PolicyContext) -> list[PolicyResult]:
        # Execute layers in order
        # If any layer fails, return immediately
        ...
```

## Outputs

- `/backend/query-pipeline/policy/__init__.py`
- `/backend/query-pipeline/policy/chain.py`
- `/backend/query-pipeline/policy/layer_base.py`
- `/backend/query-pipeline/policy/models.py`

## Acceptance Criteria

- [ ] PolicyLayerBase abstract class defined with check() method
- [ ] PolicyResult model with all fields
- [ ] PolicyChain maintains ordered layer list
- [ ] Chain stops on first failure (fail-closed)
- [ ] Each layer's duration is tracked
- [ ] Chain returns list of all results (passed layers + failing layer)
- [ ] Framework supports deterministic-only layers (L2-L10) and optional LLM layer (L1)
- [ ] L1 timeout degrades gracefully — chain continues with default "unknown" intent

## Test Requirements

- Unit tests: chain processes layers in order
- Unit tests: chain stops on first failure
- Unit tests: duration tracking works
- Unit tests: L1 timeout does not break chain
- Integration test: chain with mock layers

## Definition of Done

- Framework implemented and tested
- Ready for individual layer implementations (TASK-080 through TASK-090)
- Task status updated to `done`
