# Agent: Schema Intelligence

| Metadata | Value |
|----------|-------|
| **Agent ID** | AGENT-SCHEMA |
| **Owns Epics** | EP-006 |
| **Workspace** | `/backend/schema-intelligence/` |
| **Reads** | `/docs/Component-Design.md`, `/docs/epics/EP-006` |

---

## Responsibilities

1. Implement pluggable database connectors (PG, MySQL, Snowflake, BigQuery, DuckDB)
2. Build DDL parser for schema extraction from live databases
3. Implement LLM-based description annotator (column/table descriptions)
4. Build relationship inference engine (FK detection + heuristics)
5. Implement incremental sync orchestrator
6. Build schema-to-embedding pipeline (write to Vector Index via KE API)
7. Implement metadata-to-KE sync (write to Schema Store via KE API)

## Workspace Boundaries

```
/backend/schema-intelligence/
  __init__.py
  /connectors/
    base.py                 -> Abstract connector interface
    postgresql.py
    mysql.py
    snowflake.py
    bigquery.py
    duckdb.py
  /parsers/
    ddl_parser.py           -> sqlglot-based schema extraction
  /annotators/
    llm_describer.py        -> LLM-based description generation
  /embedders/
    embedding_service.py     -> BGE-M3 embedding service
  /inferers/
    relationship_inferer.py -> FK + heuristic inference
  orchestrator.py           -> Sync orchestrator
  config.py
```

## DO NOT Touch

- `/backend/ke/`
- `/backend/query-pipeline/`
- `/backend/api/`
- `/backend/learning/`
- `/frontend/`
- `/infra/`

## Prompts

### Connector Implementation Prompt
```
Implement the database connector interface and PostgreSQL connector.

Create base.py with:
- AbstractConnector class
- Methods: connect(), extract_schemas(), extract_tables(), extract_columns(), extract_relationships(), close()
- Standardized output format (dict with schemas, tables, columns, relationships)

Create postgresql.py with:
- PostgreSQLConnector(AbstractConnector)
- Use SQLAlchemy for connection, raw SQL for introspection
- Introspection queries for: schemas, tables, columns, constraints, FKs
- Handle connection errors, permission errors, timeout

Reference EP-006 for full requirements.
```

## Definition of Done
- All connectors implement the same interface and return standardized output
- PostgreSQL connector extracts schema from 200-table DB in < 10s
- LLM annotator generates descriptions for 50 columns in < 30s
- Relationship inference detects > 80% of actual FKs
- E2E sync: DB connection -> schema extraction -> KE Store populated
- All task status files updated
