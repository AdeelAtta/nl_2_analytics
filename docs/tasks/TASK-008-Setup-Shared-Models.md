# TASK-008: Setup Python Shared Models Package

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-008 |
| **Epic** | EP-001 |
| **Priority** | P1 |
| **Complexity** | M |
| **Dependencies** | TASK-002 (Python tooling configured) |
| **Agent Owner** | Infrastructure Agent |
| **Status** | done |

---

## Description

Create the shared Python models package (`backend/shared/models/`) containing base Pydantic v2 models, mixins, and types used by all backend services. This package serves as the single source of truth for shared data contracts across the platform.

## Inputs

- Database-Specification.md — table schemas, key entity definitions
- KnowledgeEngine-Specification.md — store interfaces, entity types
- Implementation-Plan.md §4 — directory structure for `backend/shared/models/`

## Implementation

Create the package at `backend/shared/models/`:

```
backend/shared/
  __init__.py
  models/
    __init__.py          # Exports all public types
    base.py              # BaseSchema, TimestampMixin, TenantScopedModel
    pagination.py        # PaginationParams, Page, SortOrder
    api.py               # APIResponse, ErrorResponse, APIStatus
    config.py            # BaseSettings patterns
```

### Requirements
- All models use Pydantic v2 (`BaseModel` with `model_config`)
- `BaseSchema` provides common config (frozen by default, str->datetime coercion)
- `TimestampMixin` adds `created_at` / `updated_at` with sane defaults
- `TenantScopedModel` adds `tenant_id: str` field
- `APIResponse[T]` generic wrapper: `data: T`, `status: str`, `message: str | None`
- `PaginationParams`: `page: int = 1`, `page_size: int = 20`, `sort_by: str | None`, `sort_order: SortOrder`
- `Page[T]`: `items: list[T]`, `total: int`, `page: int`, `page_size: int`, `total_pages: int`
- No business logic — purely structural base classes

## Outputs

- **Files to create**: `/backend/shared/__init__.py`, `/backend/shared/models/__init__.py`, `/backend/shared/models/base.py`, `/backend/shared/models/pagination.py`, `/backend/shared/models/api.py`
- **Files to modify**: `backend/pyproject.toml` (add shared package to workspace)

## Acceptance Criteria

- [ ] Package imports without errors: `from shared.models import BaseSchema, TimestampMixin, APIResponse`
- [ ] BaseSchema rejects unknown fields by default
- [ ] TimestampMixin auto-populates created_at on instantiation
- [ ] APIResponse serializes to correct JSON shape
- [ ] PaginationParams computes total_pages correctly
- [ ] Pydantic v2 validation works (no v1 compat warnings)
- [ ] `uv sync` resolves the shared package

## Test Requirements

- Unit tests for each base model (valid instantiation, field validation, serialization round-trip)
- Test generic type parameterization (APIResponse[str], APIResponse[dict], etc.)
- Test PaginationParams defaults and computed fields

## Definition of Done

- All files created and importable
- Unit tests pass
- `make lint && make typecheck` pass on the backend
- Task status updated to `done`
