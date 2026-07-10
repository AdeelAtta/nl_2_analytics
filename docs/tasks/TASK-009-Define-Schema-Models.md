# TASK-009: Define Schema Store Data Models

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-009 |
| **Epic** | EP-002 |
| **Priority** | P0 |
| **Complexity** | M |
| **Dependencies** | TASK-008 (Shared models package) |
| **Agent Owner** | Knowledge Engine Agent |
| **Status** | done |

---

## Description

Define Pydantic v2 data models for all Schema Store entities. These models serve as the data contract between the KE API and all consumers.

## Inputs

- Knowledge-Engine.md §3 (Data Model section)
- Shared models base classes from TASK-008

## Implementation

Define models in `/backend/ke/models/schema.py`:

```python
# Key entities (see EP-002 for full field definitions):
# Tenant, DatabaseConfig, SchemaInfo, Table, Column, Relationship
#
# Each model should:
# - Use Pydantic v2 (BaseModel with model_config)
# - Include orm_mode=True for SQLAlchemy compatibility
# - Have field validators where appropriate
# - Use UUID for primary keys (str serialized)
# - Include created_at/updated_at timestamps
```

## Outputs

- **Files to create**: `/backend/ke/models/__init__.py`, `/backend/ke/models/schema.py`
- **Files to modify**: None directly (consumers will import from here)

## Acceptance Criteria

- [ ] All entities from Knowledge-Engine.md §3 are modeled
- [ ] Models validate correctly (test with valid/invalid data)
- [ ] JSON serialization round-trips correctly
- [ ] SQLAlchemy compatibility works (orm_mode)
- [ ] Tenant isolation field present on all tenant-scoped models

## Test Requirements

- Unit tests for model validation (valid and invalid inputs)
- Unit tests for serialization/deserialization
- Test JSON Schema generation for API docs

## Definition of Done

- All models implemented and tested
- Tests pass
- Task status updated to `done`
