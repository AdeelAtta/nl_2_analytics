# Sequence Diagrams

**Version**: 1.0.0 | **Status**: Approved | **Last Updated**: 2026-07-10

---

## 1. Query Flow (Happy Path)

```
User         Public API      Intent Agent   Retriever      Planner        Generator      Validator      Policy Enf.   Executor       KE API        Target DB
 │               │               │              │              │              │              │              │              │              │              │
 │  POST /v1/query               │              │              │              │              │              │              │              │              │
 │──────────────>│               │              │              │              │              │              │              │              │              │
 │               │  JWT verify   │              │              │              │              │              │              │              │              │
 │               │──────────────│              │              │              │              │              │              │              │              │
 │               │  rate limit   │              │              │              │              │              │              │              │              │
 │               │──────────────│              │              │              │              │              │              │              │              │
 │               │  classify intent            │              │              │              │              │              │              │              │
 │               │──────────────>│              │              │              │              │              │              │              │              │
 │               │               │ intent classified           │              │              │              │              │              │              │
 │               │               │──────────────│              │              │              │              │              │              │              │
 │               │               │              │  embed query │              │              │              │              │              │              │
 │               │               │              │──────────────│              │              │              │              │              │              │
 │               │               │              │  hybrid search               │              │              │              │              │              │
 │               │               │              │───────────────────────────────────────────────────────────────────────────>│              │
 │               │               │              │  search results              │              │              │              │              │              │
 │               │               │              │<───────────────────────────────────────────────────────────────────────────│              │
 │               │               │              │  context returned            │              │              │              │              │              │
 │               │               │              │──────────────│              │              │              │              │              │              │
 │               │               │              │              │  plan query   │              │              │              │              │              │
 │               │               │              │              │──────────────│              │              │              │              │              │
 │               │               │              │              │  query plan   │              │              │              │              │              │
 │               │               │              │              │──────────────│              │              │              │              │              │
 │               │               │              │              │              │  generate SQL│              │              │              │              │
 │               │               │              │              │              │──────────────│              │              │              │              │
 │               │               │              │              │              │  SQL + candidates          │              │              │              │
 │               │               │              │              │              │──────────────│              │              │              │              │
 │               │               │              │              │              │              │  validate    │              │              │              │
 │               │               │              │              │              │              │──────────────│              │              │              │
 │               │               │              │              │              │              │  if invalid  │              │              │              │
 │               │               │              │              │              │<──────────────│              │              │              │              │
 │               │               │              │              │              │  repair(opt) │              │              │              │              │
 │               │               │              │              │              │──────────────│              │              │              │              │
 │               │               │              │              │              │              │  valid SQL   │              │              │              │
 │               │               │              │              │              │              │──────────────│              │              │              │
  │               │               │              │              │              │              │              │  10-layer    │              │              │
 │               │               │              │              │              │              │              │──────────────│              │              │
 │               │               │              │              │              │              │              │  all passed  │              │              │
 │               │               │              │              │              │              │              │──────────────│              │              │
 │               │               │              │              │              │              │              │              │  execute SQL │              │
 │               │               │              │              │              │              │              │              │──────────────│              │
 │               │               │              │              │              │              │              │              │              │  run query   │
 │               │               │              │              │              │              │              │              │              │──────────────>
 │               │               │              │              │              │              │              │              │              │  results     │
 │               │               │              │              │              │              │              │              │              │<──────────────
 │               │               │              │              │              │              │              │              │  format      │              │
 │               │               │              │              │              │              │              │              │──────────────│              │
 │               │               │              │              │              │              │              │              │  result data │              │
 │               │               │              │              │              │              │              │              │<──────────────│              │
 │               │               │              │              │              │              │              │              │              │              │
 │               │  store to history             │              │              │              │              │              │              │              │
 │               │──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────>│              │
 │               │  format response              │              │              │              │              │              │              │              │
 │               │──────────────│              │              │              │              │              │              │              │              │
 │ 200 OK + results             │              │              │              │              │              │              │              │              │
 │<──────────────│              │              │              │              │              │              │              │              │              │
 │               │               │              │              │              │              │              │              │              │              │
```

## 2. Schema Sync Flow

```
Schema Intel     Connector       Target DB       KE API (Schema)     KE API (Vector)     Embedding Svc
    │               │               │                  │                  │                   │
    │ sync(db_id)   │               │                  │                  │                   │
    │──────────────>│               │                  │                  │                   │
    │               │ connect()     │                  │                  │                   │
    │               │──────────────>│                  │                  │                   │
    │               │  connected    │                  │                  │                   │
    │               │<──────────────│                  │                  │                   │
    │               │               │                  │                  │                   │
    │               │ extract_schemas()               │                  │                   │
    │               │──────────────>│                  │                  │                   │
    │               │  schemas      │                  │                  │                   │
    │               │<──────────────│                  │                  │                   │
    │               │               │                  │                  │                   │
    │               │ extract_tables(schema)           │                  │                   │
    │               │──────────────>│                  │                  │                   │
    │               │  tables       │                  │                  │                   │
    │               │<──────────────│                  │                  │                   │
    │               │               │                  │                  │                   │
    │               │ extract_columns(table)           │                  │                   │
    │               │──────────────>│                  │                  │                   │
    │               │  columns      │                  │                  │                   │
    │               │<──────────────│                  │                  │                   │
    │               │               │                  │                  │                   │
    │               │ extract_relationships()         │                  │                   │
    │               │──────────────>│                  │                  │                   │
    │               │  rels         │                  │                  │                   │
    │               │<──────────────│                  │                  │                   │
    │               │               │                  │                  │                   │
    │               │ close()       │                  │                  │                   │
    │               │──────────────>│                  │                  │                   │
    │  data         │               │                  │                  │                   │
    │<──────────────│               │                  │                  │                   │
    │               │               │                  │                  │                   │
    │ annotate(schema)             │                  │                  │                   │
    │───────────────               │                  │                  │                   │
    │  descriptions                │                  │                  │                   │
    │<──────────────               │                  │                  │                   │
    │               │               │                  │                  │                   │
    │ embed(tables) │               │                  │                  │                   │
    │─────────────────────────────────────────────────────────────────────>│                   │
    │               │               │                  │                  │  BGE-M3 encode    │
    │               │               │                  │                  │──────────────────>│
    │               │               │                  │                  │  embeddings        │
    │               │               │                  │                  │<──────────────────│
    │               │               │                  │                  │                   │
    │ upsert_schema │               │                  │                  │                   │
    │───────────────────────────────────────────────>│                  │                   │
    │               │               │                  │  stored          │                   │
    │               │               │                  │<───────────────│                   │
    │               │               │                  │                  │                   │
    │ upsert_vectors│               │                  │                  │                   │
    │──────────────────────────────────────────────────────────────────────>│                   │
    │               │               │                  │                  │  stored            │
    │               │               │                  │                  │<──────────────────│
    │               │               │                  │                  │                   │
    │ sync_complete │               │                  │                  │                   │
    │<──────────────               │                  │                  │                   │
```

## 3. Learning Loop Flow (Batch Cycle)

```
Scheduler        Feedback Store    Validator         Q&A Builder      Schema Enricher   Pattern Miner     KE API     
    │                 │               │                  │                  │               │               │
    │ tick (5 min)    │               │                  │                  │               │               │
    │────────────────>│               │                  │                  │               │               │
    │                 │               │                  │                  │               │               │
    │ poll pending    │               │                  │                  │               │               │
    │────────────────>│               │                  │                  │               │               │
    │                 │ pending items │                  │                  │               │               │
    │                 │──────────────>│                  │                  │               │               │
    │                 │               │                  │                  │               │               │
    │                 │               │ validate batch   │                  │               │               │
    │                 │               │─────────────────│                  │               │               │
    │                 │               │ valid items      │                  │               │               │
    │                 │               │─────────────────│                  │               │               │
    │                 │               │  filter: quality > 0.3              │               │               │
    │                 │               │─────────────────│                  │               │               │
    │                 │               │                  │                  │               │               │
    │                 │               │ Q&A items        │                  │               │               │
    │                 │               │─────────────────>│                  │               │               │
    │                 │               │                  │  build pairs     │               │               │
    │                 │               │                  │─────────────────│               │               │
    │                 │               │                  │  pairs           │               │               │
    │                 │               │                  │                 >│               │               │
    │                 │               │ enricher items   │                  │               │               │
    │                 │               │─────────────────│                  >│               │               │
    │                 │               │                  │                  │  enrich desc  │               │
    │                 │               │                  │                  │───────────────│               │
    │                 │               │                  │                  │  enriched     │               │
    │                 │               │                  │                  │<──────────────│               │
    │                 │               │                  │                  │               │               │
    │                 │               │ pattern items    │                  │               │               │
    │                 │               │─────────────────│                  │               >│               │
    │                 │               │                  │                  │               │  mine patterns |
    │                 │               │                  │                  │               │───────────────>│
    │                 │               │                  │                  │               │  patterns      │
    │                 │               │                  │                  │               │<───────────────│
    │                 │               │                  │                  │               │               │
    │                 │               │                  │                  │               │               │
    │                 │               │ batch write to KE                   │               │               │
    │                 │               │────────────────────────────────────────────────────────────────────>│
    │                 │               │                  │                  │               │               │  updated
    │                 │               │                  │                  │               │               │<───────────────
    │                 │               │                  │                  │               │               │
    │                 │ mark processed│                  │                  │               │               │
    │                 │<──────────────│                  │                  │               │               │
    │                 │               │                  │                  │               │               │
    │ cycle complete  │               │                  │                  │               │               │
    │<────────────────│               │                  │                  │               │               │
```

## 4. Error Flow (Policy Enforcement Rejection)

```
User         Public API      Policy Enforcement    Audit Store
 │               │               │                   │
 │  POST /v1/query               │                   │
 │──────────────>│               │                   │
 │               │  run layers   │                   │
 │               │──────────────>│                   │
 │               │               │  Intent Classify: pass│
 │               │               │  SQL Sanitize: pass│
 │               │               │  RBAC: FAIL      │
 │               │               │  (unauthorized    │
 │               │               │   table: hr.employees)
 │               │               │                   │
 │               │               │  log to audit     │
 │               │               │──────────────────>│
 │               │               │                   │
 │               │ policy_rejected                  │
 │               │<──────────────│                   │
 │               │               │                   │
 │  ERR-012      │               │                   │
 │<──────────────│               │                   │
 │               │               │                   │
```

## 5. Cold Start Flow

```
Admin           Schema Intel      Connector        Target DB        KE API
  │                 │               │                 │               │
  │ connect DB      │               │                 │               │
  │────────────────>│               │                 │               │
  │                 │ introspect    │                 │               │
  │                 │──────────────>│                 │               │
  │                 │               │ extract DDL     │               │
  │                 │               │────────────────>│               │
  │                 │               │ schemas + DDL   │               │
  │                 │               │<────────────────│               │
  │                 │               │                 │               │
  │                 │ generate synthetic descriptions (LLM)           │
  │                 │────────────────────────────────│               │
  │                 │ embed all schema elements                       │
  │                 │────────────────────────────────│               │
  │                 │                 │               │               │
  │                 │ store to KE    │               │               │
  │                 │──────────────────────────────────────────────>│
  │                 │  1. Schema Store (tables, columns, rels)      │
  │                 │  2. Vector Index (embeddings)                  │
  │                 │  3. Graph Store (nodes)                        │
  │                 │                 │               │               │
  │ ready           │                 │               │               │
  │<────────────────│                 │               │               │
```
