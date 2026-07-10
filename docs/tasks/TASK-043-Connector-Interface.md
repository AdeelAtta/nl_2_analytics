# TASK-043: Implement Database Connector Interface

| Metadata | Value |
|----------|-------|
| **Task ID** | TASK-043 |
| **Epic** | EP-006 |
| **Priority** | P0 |
| **Complexity** | M |
| **Dependencies** | TASK-008 |
| **Agent Owner** | Schema Intelligence Agent |
| **Status** | backlog |

---

## Description

Implement the abstract database connector interface that all database-specific connectors will implement. This defines the contract for schema introspection.

## Inputs

- Component-Design.md §2 (Schema Intelligence section)
- Shared models from TASK-008

## Implementation

Create `/backend/schema-intelligence/connectors/base.py`:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

@dataclass
class ConnectorConfig:
    host: str
    port: int
    database: str
    username: str
    password: str  # Never logged
    schema_filter: list[str] | None = None
    ssl: bool = True
    timeout_seconds: int = 30

@dataclass
class ExtractedSchema:
    database_name: str
    db_type: str
    schemas: list[ExtractedSchemaInfo]

@dataclass
class ExtractedSchemaInfo:
    name: str
    tables: list[ExtractedTable]

@dataclass
class ExtractedTable:
    name: str
    columns: list[ExtractedColumn]
    ddl: str

@dataclass
class ExtractedColumn:
    name: str
    ordinal_position: int
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    default_value: str | None
    foreign_key: ForeignKeyRef | None

@dataclass
class ForeignKeyRef:
    ref_table: str
    ref_column: str

class BaseConnector(ABC):
    @abstractmethod
    async def connect(self, config: ConnectorConfig) -> None: ...
    
    @abstractmethod
    async def extract_schema(self) -> ExtractedSchema: ...
    
    @abstractmethod
    async def extract_tables(self, schema_name: str) -> list[ExtractedTable]: ...
    
    @abstractmethod
    async def extract_relationships(self) -> list[Relationship]: ...
    
    @abstractmethod
    async def close(self) -> None: ...
    
    @abstractmethod
    async def __aenter__(self): ...
    
    @abstractmethod
    async def __aexit__(self, *args): ...
```

## Outputs

- `/backend/schema-intelligence/connectors/__init__.py`
- `/backend/schema-intelligence/connectors/base.py`

## Acceptance Criteria

- [ ] All abstract methods defined with clear signatures
- [ ] Data classes cover all necessary schema information
- [ ] Async context manager protocol implemented
- [ ] No implementation details (pure interface)
- [ ] Docstrings describe contract for implementors

## Test Requirements

- Unit tests verifying interface contract (subclass must implement all methods)
- Test data classes with sample data

## Definition of Done

- Interface defined and documented
- Tests verify the contract
- Task status updated to `done`
