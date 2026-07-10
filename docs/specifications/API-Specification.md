# API Specification

**Version**: 1.0.0 | **Status**: Approved | **Last Updated**: 2026-07-10

**Document Owner**: Chief API Architect

**Cross-References**:
- [AI-Agent-Specification.md](AI-Agent-Specification.md) — Agent pipeline, QueryState schema
- [Workflow-Orchestrator-Specification.md](Workflow-Orchestrator-Specification.md) — Pipeline lifecycle, SSE streaming integration
- [Database-Specification.md](Database-Specification.md) — Database schemas for query history, audit, feedback
- [Security-Specification.md](Security-Specification.md) — Auth, RBAC, error codes
- [Observability-Specification.md](Observability-Specification.md) — API metrics, SLOs, alerting
- [Frontend-Specification.md](Frontend-Specification.md) — Frontend API consumption patterns
- [Performance-Budgets.md](Performance-Budgets.md) — API latency budgets
- [Sequence-Diagrams.md](Sequence-Diagrams.md) — API interaction flows

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [API Overview](#2-api-overview)
3. [Authentication & Authorization](#3-authentication--authorization)
4. [API Versioning](#4-api-versioning)
5. [Standard Patterns](#5-standard-patterns)
6. [Public REST API (port 8100)](#6-public-rest-api-port-8100)
7. [Knowledge Engine API (port 8200, Internal)](#7-knowledge-engine-api-port-8200-internal)
8. [Agent APIs (Internal)](#8-agent-apis-internal)
9. [Event API (Internal, Async)](#9-event-api-internal-async)
10. [WebSocket API](#10-websocket-api)
11. [Streaming API](#11-streaming-api)
12. [Error Catalog](#12-error-catalog)
13. [Rate Limiting](#13-rate-limiting)
14. [Multi-Tenancy](#14-multi-tenancy)
15. [Idempotency](#15-idempotency)
16. [Retry Behavior](#16-retry-behavior)
17. [Version History](#17-version-history)
18. [Future Compatibility](#18-future-compatibility)

---

## 1. Design Philosophy

### Principles

1. **Contract-first**: Every API has a defined contract before implementation begins
2. **Consistent patterns**: Every endpoint follows the same patterns for pagination, filtering, errors, and versioning
3. **Self-describing**: OpenAPI specs are auto-generated and browsable at `/docs`
4. **Backward compatible**: Minor versions add fields only, never remove or rename
5. **Fail closed**: Security failures, validation failures, and policy enforcement violations return clear errors, never partial data
6. **Observable by default**: Every endpoint emits metrics, logs, and traces
7. **Tenant-aware**: Every tenant-scoped endpoint requires `X-Tenant-Id`

### API Layers

```
External                           Internal (service mesh)
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Public API  │────▶│  Query       │────▶│  Agent APIs │
│  (port 8100) │     │  Pipeline   │     │  (LangGraph)│
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       │                    ▼                    │
       │           ┌─────────────┐              │
       └──────────▶│  KE API      │◀─────────────┘
                   │  (port 8200) │
                   └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Event Bus  │
                   │  (Redis)    │
                   └─────────────┘
```

---

## 2. API Overview

| API Layer | Port | Protocol | Audience | Auth | Base Path |
|-----------|------|----------|----------|------|-----------|
| Public REST | 8100 | HTTPS | Users, CLI, SDK | JWT or API Key | `/v1/` |
| Knowledge Engine | 8200 | HTTP/gRPC | Internal services | Service Token | `/v1/` |
| Agent | — | LangGraph (in-process) | Pipeline agents | None (in-process) | — |
| Event | — | Redis Pub/Sub | Internal services | Network policy | — |
| WebSocket | 8100 | WSS | Frontend | JWT (handshake) | `/ws/v1/` |
| Streaming | 8100 | SSE | Frontend | JWT | `/v1/stream/` |

---

## 3. Authentication & Authorization

### 3.1 Authentication Methods

#### JWT Bearer Token

**Purpose**: User authentication. Obtained via login or API key exchange.

**Header**: `Authorization: Bearer <token>`

**Token Claims**:
```json
{
  "sub": "usr_001",
  "tenant_id": "tnt_001",
  "role": "admin",
  "permissions": ["queries:execute", "databases:manage"],
  "iat": 1720627200,
  "exp": 1720630800,
  "jti": "unique_token_id"
}
```

**Expiry**: 30 minutes (production), 24 hours (dev)
**Refresh**: POST `/v1/auth/refresh` returns new JWT
**Revocation**: Server-side blocklist checked on every request

#### API Key

**Purpose**: Service-to-service, CLI, SDK integration.

**Header**: `X-API-Key: ak_live_abcdef123456`

**Key Format**: `ak_live_<32 hex chars>` or `ak_test_<32 hex chars>`
**Key Permissions**: Inherit creating user's role
**Key Rotation**: Keys have no expiry but can be revoked

#### Service Token

**Purpose**: Internal service-to-service authentication (KE API).

**Header**: `X-Service-Token: st_<uuid>`

**Token Distribution**: Injected via K8s Secret
**Token Rotation**: Every 30 days
**Scope**: Fixed to calling service identity

#### Tenant Context

**Header**: `X-Tenant-Id: tnt_001`

**Required**: All tenant-scoped endpoints
**Validation**: Must match JWT claim `tenant_id`
**Propagation**: Passed through to KE API on internal calls

### 3.2 Authorization (RBAC)

| Role | Permissions | Scope |
|------|-------------|-------|
| `admin` | Full access, team management, billing | Tenant |
| `member` | Execute queries, view history, manage own settings | Tenant |
| `viewer` | Execute read-only queries, view schemas | Tenant |
| `api` | Execute queries via API key | Tenant |

**Permission check flow**:
1. Extract `role` from JWT claims
2. Look up role permissions from `config_store` (KE API)
3. If endpoint requires permission not in role's set -> 403 FORBIDDEN

---

## 4. API Versioning

### Strategy: URL-prefixed

```
/v1/query         # Current major version
/v2/query         # Next major version (breaking changes)
```

### Rules

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| New endpoint | Minor (no URL change) | `POST /v1/query/explain` |
| New optional field | Minor | Adding `options.dry_run` to request |
| New required field | Major (`/v2/`) | Making `database_id` required |
| Field removal | Major | Removing a deprecated field |
| Behavior change | Major | Response format changes |
| Field type change | Major | `status` from string to enum |

### Deprecation Policy

1. Deprecated endpoints return `Sunset` header with migration date
2. Old version supported for 6 months after replacement ships
3. Deprecation logged to audit store with caller identity
4. Breaking changes announced 3 months before removal

---

## 5. Standard Patterns

### 5.1 Response Envelope

```json
{
  "status": "ok",
  "data": {},
  "meta": {
    "request_id": "req_abc123",
    "took_ms": 142,
    "api_version": "1.0.0"
  }
}
```

**For lists**:
```json
{
  "status": "ok",
  "data": [],
  "meta": {
    "request_id": "req_abc123",
    "took_ms": 45,
    "api_version": "1.0.0",
    "pagination": {
      "page": 1,
      "page_size": 50,
      "total": 142,
      "total_pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 5.2 Error Envelope

```json
{
  "status": "error",
  "error": {
    "code": "ERR-042",
    "message": "Human-readable error description",
    "details": {
      "field": "database_id",
      "reason": "Database not found or not accessible"
    },
    "request_id": "req_abc123",
    "docs_url": "https://docs.opencode.ai/errors/ERR-042"
  }
}
```

### 5.3 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `page_size` | integer | 50 | Items per page (max 200) |
| `sort_by` | string | `created_at` | Sort field |
| `sort_order` | enum | `desc` | `asc` or `desc` |

**Response** includes `meta.pagination` (see 5.1).

### 5.4 Filtering

**Query parameter syntax**: `?filter=<field>:<operator>:<value>`

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `?filter=status:eq:success` |
| `neq` | Not equals | `?filter=status:neq:failed` |
| `gt` | Greater than | `?filter=execution_time_ms:gt:5000` |
| `gte` | Greater than or equal | `?filter=created_at:gte:2026-06-01` |
| `lt` | Less than | `?filter=row_count:lt:100` |
| `lte` | Less than or equal | `?filter=cost:lte:0.01` |
| `in` | In list | `?filter=status:in:success,failed` |
| `contains` | Substring | `?filter=natural_query:contains:revenue` |

**Multiple filters**: `?filter=status:eq:success&filter=cost:gt:0.001`

### 5.5 Search

**Parameter**: `?q=<search_term>`

Applies full-text search across relevant fields. Available on:
- Query history: searches `natural_query` and `generated_sql`
- Schemas: searches table names and column names
- Feedback: searches comments

### 5.6 Batch Operations

**Pattern**: POST `/v1/<resource>/batch`

**Request**:
```json
{
  "operations": [
    { "method": "POST", "path": "/v1/feedback", "body": { ... } },
    { "method": "POST", "path": "/v1/feedback", "body": { ... } }
  ]
}
```

**Response**:
```json
{
  "results": [
    { "status": 201, "data": { "id": "fb_001" }, "request_id": "req_001" },
    { "status": 201, "data": { "id": "fb_002" }, "request_id": "req_002" }
  ],
  "meta": { "total": 2, "succeeded": 2, "failed": 0 }
}
```

### 5.7 Async Jobs

**Pattern**: Long-running operations return 202 Accepted with polling URL.

**Response 202**:
```json
{
  "status": "accepted",
  "data": {
    "job_id": "job_001",
    "status": "queued",
    "poll_url": "/v1/jobs/job_001",
    "cancel_url": "/v1/jobs/job_001/cancel",
    "estimated_completion_ms": 5000
  },
  "meta": { "request_id": "req_abc" }
}
```

**Polling**: GET `/v1/jobs/{job_id}`

**Response**:
```json
{
  "status": "ok",
  "data": {
    "job_id": "job_001",
    "status": "completed",
    "progress": 1.0,
    "result": { ... },
    "started_at": "2026-07-10T10:00:00Z",
    "completed_at": "2026-07-10T10:00:05Z"
  }
}
```

### 5.8 Idempotency

**Header**: `Idempotency-Key: <uuid>`

**Supported on**: POST/PATCH endpoints (query, feedback, database creation)
**TTL**: 24 hours after first request
**Response**: Returns cached response for duplicate keys within TTL
**Behavior**: If first request is still processing, returns 409 Conflict

### 5.9 Request IDs

**Header**: `X-Request-Id: req_<ulid>` (auto-generated if not provided)

Propagated through all downstream service calls (KE API, agents, target DB). Logged in all log entries. Returned in all responses.

### 5.10 Content Type

**Request**: `Content-Type: application/json`
**Response**: `application/json`

Binary responses (file downloads, exports): `application/octet-stream` or `text/csv`

---

## 6. Public REST API (port 8100)

### 6.1 Authentication Endpoints

#### POST /v1/auth/login

**Purpose**: Authenticate user with email/password. Returns JWT.

**Request**:
```json
{
  "email": "user@company.com",
  "password": "securePassword123!",
  "remember_me": false
}
```

**Validation**:
| Field | Rule |
|-------|------|
| email | Required, valid email format, max 255 chars |
| password | Required, min 8 chars, max 128 chars |

**Response 200**:
```json
{
  "token_type": "Bearer",
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "expires_in": 1800,
  "refresh_token": "rt_abc123",
  "user": {
    "id": "usr_001",
    "email": "user@company.com",
    "name": "User Name",
    "avatar_url": "https://avatars.opencode.ai/usr_001",
    "role": "admin",
    "tenant_id": "tnt_001",
    "created_at": "2026-01-15T10:00:00Z"
  }
}
```

**Errors**:
| Status | Code | Condition |
|--------|------|-----------|
| 401 | ERR-004 | Invalid email or password |
| 429 | ERR-003 | Too many login attempts |

**Security**: Rate limited (5 attempts/min per IP). Credentials never logged.

**Performance**: P50 < 200ms, P95 < 500ms

---

#### POST /v1/auth/refresh

**Purpose**: Exchange refresh token for new JWT.

**Request**:
```json
{
  "refresh_token": "rt_abc123"
}
```

**Response 200**: Same as login (new access_token + new refresh_token)

**Errors**:
| Status | Code | Condition |
|--------|------|-----------|
| 401 | ERR-004 | Invalid or expired refresh token |

---

#### POST /v1/auth/api-key

**Purpose**: Exchange API key for short-lived JWT.

**Request**:
```json
{
  "api_key": "ak_live_abcdef1234567890abcdef12345678"
}
```

**Response 200**:
```json
{
  "token_type": "Bearer",
  "access_token": "eyJhbG...",
  "expires_in": 300,
  "scope": "queries:execute"
}
```

---

#### POST /v1/auth/logout

**Purpose**: Invalidate current JWT. Adds token to blocklist.

**Headers**: `Authorization: Bearer <token>`

**Response 204**: No content

---

### 6.2 Query Endpoints

#### POST /v1/query

**Purpose**: Submit a natural language query for execution.

**Request**:
```json
{
  "query": "Show me total revenue by customer for last quarter",
  "database_id": "db_001",
  "conversation_id": "conv_001",
  "options": {
    "timeout_seconds": 30,
    "max_rows": 1000,
    "dry_run": false,
    "model_tier": "auto",
    "temperature": 0.1,
    "max_sql_candidates": 3
  }
}
```

**Validation**:
| Field | Rule |
|-------|------|
| query | Required, 1-4000 chars, non-empty after trim |
| database_id | Required, valid UUID format |
| conversation_id | Optional, UUID |
| options.timeout_seconds | Optional, 5-120, default 30 |
| options.max_rows | Optional, 1-10000, default 1000 |
| options.dry_run | Optional, boolean, default false |
| options.model_tier | Optional, enum: auto, simple, medium, complex |
| options.temperature | Optional, 0.0-1.0, default 0.1 |

**Response 200** (sync, simple query):
```json
{
  "id": "qry_001",
  "status": "success",
  "sql": "SELECT c.name, SUM(o.total) AS total_revenue\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nWHERE o.created_at >= '2026-04-01'\nGROUP BY c.name\nORDER BY total_revenue DESC\nLIMIT 100",
  "results": [
    { "name": "Acme Corp", "total_revenue": 1500000.00 },
    { "name": "Beta Inc", "total_revenue": 980000.00 }
  ],
  "columns": [
    { "name": "name", "type": "varchar", "nullable": false },
    { "name": "total_revenue", "type": "decimal", "nullable": true }
  ],
  "row_count": 2,
  "truncated": false,
  "execution": {
    "total_ms": 2340,
    "breakdown_ms": {
      "intent": 120,
      "retrieval": 180,
      "planning": 340,
      "generation": 1100,
      "validation": 80,
      "policy_enforcement": 150,
      "execution": 430
    }
  },
  "cost": {
    "total": 0.0024,
    "breakdown": {
      "inference": 0.0022,
      "embedding": 0.00001,
      "storage": 0.00019
    },
    "model_used": "qwen2.5-72b"
  },
  "policy_results": [
    { "layer": "intent_classification", "passed": true, "ms": 15 },
    { "layer": "sql_sanitization", "passed": true, "ms": 5 },
    { "layer": "rbac", "passed": true, "ms": 10 },
    { "layer": "cost_ceiling", "passed": true, "metric": "estimated_rows:150", "ms": 8 },
    { "layer": "sql_validation", "passed": true, "ms": 25 },
    { "layer": "read_only", "passed": true, "ms": 3 },
    { "layer": "audit_logging", "passed": true, "ms": 24 },
    { "layer": "data_classification", "passed": true, "pii_detected": false, "ms": 20 },
    { "layer": "advanced_validation", "passed": true, "ms": 15 },
    { "layer": "anomaly_detection", "passed": true, "anomaly_score": 0.02, "ms": 30 }
  ],
  "feedback_token": "fb_token_abc"
}
```

**Response 202** (async, complex query):
```json
{
  "id": "qry_002",
  "status": "processing",
  "poll_url": "/v1/query/qry_002/status",
  "cancel_url": "/v1/query/qry_002/cancel",
  "estimated_ms": 8000
}
```

**Errors**:
| Status | Code | Condition |
|--------|------|-----------|
| 400 | ERR-007 | Validation error (bad query, bad options) |
| 400 | ERR-014 | Intent classification failed |
| 400 | ERR-015 | Query plan infeasible |
| 400 | ERR-011 | Query too costly (exceeds cost ceiling) |
| 400 | ERR-012 | Policy enforcement rejection (unsafe query) |
| 404 | ERR-013 | Database not synced |
| 503 | ERR-009 | Target database unreachable |
| 503 | ERR-016 | Model inference timeout |
| 503 | ERR-017 | Model unavailable |

**Idempotency**: Supported (Idempotency-Key). Same key within 24h returns cached result.

**Performance**: Simple: P50 < 2s, P95 < 5s. Complex: P50 < 5s, P95 < 12s.

**Dependencies**: Intent Agent, Retriever, Planner, Generator, Validator, Policy Enforcement, Executor, KE API

---

#### GET /v1/query/{query_id}

**Purpose**: Poll query status or retrieve completed result.

**Path Parameters**: `query_id` (UUID)

**Response 200** (completed):
```json
{
  "id": "qry_002",
  "status": "success",
  "sql": "...",
  "results": [],
  "columns": [],
  "row_count": 0,
  "execution": {},
  "cost": {},
  "policy_results": []
}
```

**Response 200** (processing):
```json
{
  "id": "qry_002",
  "status": "processing",
  "stage": "generating",
  "progress": 0.6,
  "estimated_ms": 3000
}
```

**Errors**:
| Status | Code | Condition |
|--------|------|-----------|
| 404 | ERR-006 | Query not found or not accessible |

---

#### POST /v1/query/validate

**Purpose**: Validate a query without executing. Runs intent + retrieval + planning + policy enforcement, but not generation or execution.

**Request**:
```json
{
  "query": "Show revenue by customer",
  "database_id": "db_001"
}
```

**Response 200**:
```json
{
  "valid": true,
  "sql": "SELECT c.name, SUM(o.total) AS total_revenue\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.name\nORDER BY total_revenue DESC",
  "estimated_rows": 150,
  "estimated_cost": 0.0003,
  "intent": {
    "type": "aggregate",
    "domain": "sales",
    "confidence": 0.95
  },
  "policy_results": [
    { "layer": "intent_classification", "passed": true },
    { "layer": "sql_sanitization", "passed": true },
    { "layer": "rbac", "passed": true },
    { "layer": "cost_ceiling", "passed": true, "estimated_rows": 150 },
    { "layer": "sql_validation", "passed": true },
    { "layer": "read_only", "passed": true },
    { "layer": "audit_logging", "passed": true },
    { "layer": "data_classification", "passed": true },
    { "layer": "advanced_validation", "passed": true },
    { "layer": "anomaly_detection", "passed": true }
  ],
  "warnings": [
    "orders table has no index on created_at - full scan expected"
  ]
}
```

**Response 200** (invalid):
```json
{
  "valid": false,
  "policy_results": [
    { "layer": "intent_classification", "passed": true },
    { "layer": "rbac", "passed": false, "reason": "Table 'hr.employees' not in authorized schemas for this user" }
  ],
  "errors": [
    { "code": "ERR-012", "message": "RBAC policy layer blocked access to table: hr.employees" }
  ]
}
```

---

#### POST /v1/query/{query_id}/cancel

**Purpose**: Cancel a running query.

**Response 200**:
```json
{
  "id": "qry_002",
  "status": "cancelled",
  "cancelled_at": "2026-07-10T10:05:00Z"
}
```

---

#### GET /v1/query/history

**Purpose**: List query history with filtering, pagination, and search.

**Query Parameters**: See §5.3 (Pagination), §5.4 (Filtering), §5.5 (Search)

**Supported filters**: `status`, `database_id`, `model_used`, `execution_time_ms`, `cost`, `created_at`

**Response 200**:
```json
{
  "data": [
    {
      "id": "qry_001",
      "natural_query": "Show revenue by customer",
      "status": "success",
      "execution_time_ms": 2340,
      "cost": 0.0024,
      "model_used": "qwen2.5-72b",
      "database_name": "Production",
      "row_count": 42,
      "feedback_rating": "positive",
      "created_at": "2026-07-10T09:55:00Z"
    }
  ],
  "meta": { "pagination": { "page": 1, "page_size": 50, "total": 142 } }
}
```

---

#### DELETE /v1/query/history/{query_id}

**Purpose**: Soft-delete a query from history. Admin only.

**Response 204**: No content

**Idempotency**: Supported

---

### 6.3 Database Connection Endpoints

#### GET /v1/databases

**Purpose**: List connected databases for the authenticated tenant.

**Response 200**:
```json
{
  "data": [
    {
      "id": "db_001",
      "name": "Production DB",
      "db_type": "postgresql",
      "host": "prod-db.internal",
      "port": 5432,
      "database": "main",
      "schema_filter": ["public", "sales"],
      "sync_status": "synced",
      "table_count": 142,
      "last_synced_at": "2026-07-10T08:00:00Z",
      "created_at": "2026-06-01T10:00:00Z"
    }
  ]
}
```

#### POST /v1/databases

**Purpose**: Connect a new database.

**Request**:
```json
{
  "name": "Production DB",
  "db_type": "postgresql",
  "host": "prod-db.internal",
  "port": 5432,
  "database": "main",
  "username": "opencode_user",
  "password": "temporary_password",
  "ssl": true,
  "schema_filter": ["public", "sales"],
  "options": {
    "connection_timeout_seconds": 10,
    "pool_size": 5,
    "statement_timeout_ms": 30000
  }
}
```

**Validation**:
| Field | Rule |
|-------|------|
| name | Required, 1-255 chars |
| db_type | Required, enum: postgresql, mysql, snowflake, bigquery, duckdb |
| host | Required for PG/MySQL |
| port | Required for PG/MySQL, 1-65535 |
| database | Required |
| username | Required |
| password | Required, never stored in plaintext. SHA-256 hash stored for dedup. |

**Response 201**:
```json
{
  "id": "db_002",
  "name": "Production DB",
  "db_type": "postgresql",
  "sync_status": "pending",
  "sync_url": "/v1/databases/db_002/sync"
}
```

**Errors**:
| Status | Code | Condition |
|--------|------|-----------|
| 400 | ERR-007 | Validation error |
| 400 | ERR-009 | Database unreachable (connection test failed) |

**Async flow**: Returns 201 immediately. Schema sync runs async. Poll `GET /v1/databases/{id}` for sync_status.

**Idempotency**: Supported (prevents duplicate connections).

---

#### GET /v1/databases/{database_id}

**Purpose**: Get detailed database info.

#### PATCH /v1/databases/{database_id}

**Purpose**: Update database connection. Fields are optional (partial update).

**Response 200**: Updated database object.

#### DELETE /v1/databases/{database_id}

**Purpose**: Disconnect and remove database. All associated schemas, history, and cached data are deleted.

**Response 204**

#### POST /v1/databases/{database_id}/sync

**Purpose**: Trigger immediate schema re-sync.

**Response 202**:
```json
{
  "status": "accepted",
  "data": {
    "job_id": "job_003",
    "status": "queued",
    "poll_url": "/v1/jobs/job_003"
  }
}
```

#### POST /v1/databases/test

**Purpose**: Test a database connection without saving.

**Request**: Same as POST /v1/databases but without saving.

**Response 200**:
```json
{
  "success": true,
  "latency_ms": 12,
  "server_version": "PostgreSQL 16.3",
  "schema_count": 3,
  "table_count": 142
}
```

---

### 6.4 Schema Endpoints

#### GET /v1/databases/{database_id}/schemas

**Purpose**: Get full schema tree for a database.

**Response 200**:
```json
{
  "database_name": "Production",
  "schemas": [
    {
      "name": "public",
      "tables": [
        {
          "id": "tbl_001",
          "name": "customers",
          "description": "Customer master data",
          "row_count_estimate": 50000,
          "columns": [
            {
              "name": "id",
              "type": "uuid",
              "nullable": false,
              "is_primary_key": true,
              "default_value": "gen_random_uuid()",
              "description": "Primary key, auto-generated",
              "foreign_key": null
            },
            {
              "name": "name",
              "type": "varchar(255)",
              "nullable": false,
              "is_primary_key": false,
              "default_value": null,
              "description": "Customer company name",
              "foreign_key": null
            }
          ],
          "relationships": [
            {
              "source_column": "id",
              "target_table": "orders",
              "target_column": "customer_id",
              "type": "foreign_key",
              "confidence": 1.0
            }
          ]
        }
      ]
    }
  ]
}
```

#### GET /v1/databases/{database_id}/tables/{table_id}

**Purpose**: Get detailed table information including sample data.

**Response 200**: Table details + sample data (top 20 rows).

#### GET /v1/databases/{database_id}/search

**Purpose**: Search across all tables and columns in a database.

**Query Parameters**: `?q=customer&type=table,column`

**Response 200**:
```json
{
  "results": [
    { "type": "table", "name": "customers", "schema": "public", "relevance": 0.95 },
    { "type": "column", "name": "customer_id", "table": "orders", "schema": "public", "relevance": 0.85 }
  ]
}
```

---

### 6.5 Feedback Endpoints

#### POST /v1/feedback

**Purpose**: Submit feedback for a query result.

**Request**:
```json
{
  "query_id": "qry_001",
  "rating": "negative",
  "corrected_sql": "SELECT c.name, SUM(o.total) AS total_revenue\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nWHERE o.created_at >= '2026-04-01'\nGROUP BY c.name\nORDER BY total_revenue DESC",
  "comment": "The generated SQL used the wrong date filter - it used last month instead of last quarter",
  "category": "wrong_filter",
  "feedback_token": "fb_token_abc"
}
```

**Validation**:
| Field | Rule |
|-------|------|
| query_id | Required, must exist and belong to this user |
| rating | Required, enum: positive, negative, partial |
| corrected_sql | Optional, valid SQL if provided, max 10000 chars |
| comment | Optional, max 2000 chars |
| feedback_token | Optional, must match token from query response |

**Response 201**:
```json
{
  "id": "fb_001",
  "status": "accepted",
  "message": "Thank you! Your feedback helps improve results."
}
```

**Idempotency**: Supported (prevents duplicate feedback on same query by same user).

---

### 6.6 Admin Endpoints

#### GET /v1/admin/usage

**Purpose**: Get tenant usage metrics. Admin only.

**Query Parameters**: ?period=last_7_days (enum: today, yesterday, last_7_days, last_30_days, this_month, custom) &start=2026-07-01&end=2026-07-10

**Response 200**:
```json
{
  "queries": { "total": 1234, "success": 1185, "failed": 32, "rejected": 17 },
  "users": { "active": 12, "total": 15 },
  "cost": { "total": 3.42, "avg_per_query": 0.0028 },
  "latency": { "p50_ms": 2100, "p95_ms": 6500, "p99_ms": 12000 },
  "databases": { "connected": 3, "synced": 3 },
  "models": {
    "sqlcoder-7b-2": { "queries": 617, "cost": 0.19 },
    "qwen2.5-72b": { "queries": 432, "cost": 0.86 },
    "deepseek-v3": { "queries": 123, "cost": 1.23 },
    "gpt-4o": { "queries": 62, "cost": 1.24 }
  },
  "daily_breakdown": [
    { "date": "2026-07-04", "queries": 180, "success_rate": 0.96, "cost": 0.52 },
    { "date": "2026-07-05", "queries": 195, "success_rate": 0.97, "cost": 0.48 }
  ]
}
```

#### GET /v1/admin/team

**Purpose**: List team members. Admin only.

**Response 200**:
```json
{
  "members": [
    {
      "id": "usr_001",
      "email": "admin@company.com",
      "name": "Admin User",
      "role": "admin",
      "status": "active",
      "queries_this_month": 450,
      "joined_at": "2026-01-15T10:00:00Z",
      "last_active_at": "2026-07-10T09:55:00Z"
    }
  ]
}
```

#### POST /v1/admin/team/invite

**Purpose**: Invite a team member.

**Request**:
```json
{
  "email": "newuser@company.com",
  "name": "New User",
  "role": "member"
}
```

**Response 201**:
```json
{
  "invite_id": "inv_001",
  "email": "newuser@company.com",
  "status": "pending",
  "invite_url": "https://app.opencode.ai/invite/abc123",
  "expires_at": "2026-07-17T10:00:00Z"
}
```

#### PATCH /v1/admin/team/{user_id}/role

**Purpose**: Change user role.

**Request**:
```json
{
  "role": "admin"
}
```

**Response 200**

#### DELETE /v1/admin/team/{user_id}

**Purpose**: Remove team member.

**Response 204**

#### GET /v1/admin/billing

**Purpose**: Get billing information.

**Response 200**:
```json
{
  "plan": "pro",
  "status": "active",
  "seats": { "total": 10, "used": 8 },
  "current_period": { "start": "2026-07-01", "end": "2026-07-31" },
  "amount_due": 1500.00,
  "payment_method": { "brand": "visa", "last4": "4242", "expires": "2028-12" },
  "invoices": [
    { "id": "inv_001", "date": "2026-07-01", "amount": 1500.00, "status": "paid", "pdf_url": "..." }
  ]
}
```

---

### 6.7 Job Endpoints

#### GET /v1/jobs/{job_id}

**Purpose**: Poll async job status.

**Response 200**:
```json
{
  "job_id": "job_003",
  "type": "schema_sync",
  "status": "completed",
  "progress": 1.0,
  "result": { "tables_synced": 142, "columns_synced": 2840 },
  "started_at": "2026-07-10T10:00:00Z",
  "completed_at": "2026-07-10T10:00:05Z",
  "estimated_completion_ms": 5000
}
```

#### POST /v1/jobs/{job_id}/cancel

**Purpose**: Cancel a running job.

**Response 200**:
```json
{
  "job_id": "job_003",
  "status": "cancelled"
}
```

**Job Statuses**: `queued`, `running`, `completed`, `failed`, `cancelled`

---

## 7. Knowledge Engine API (port 8200, Internal)

### 7.1 Overview

All KE API endpoints:
- Require `X-Service-Token` header
- Require `X-Tenant-Id` header (except global config/tenants)
- Listen on port 8200
- Are NOT exposed to the public internet
- Use same error envelope as Public API

### 7.2 Schema Store

#### GET /v1/schemas

**Purpose**: List all schemas for a tenant.

**Headers**: X-Tenant-Id, X-Service-Token

**Response 200**:
```json
{
  "data": [
    {
      "id": "sch_001",
      "database_id": "db_001",
      "name": "public",
      "table_count": 25,
      "created_at": "2026-06-01T10:00:00Z"
    }
  ]
}
```

#### GET /v1/schemas/{schema_id}/tables

**Purpose**: List all tables in a schema.

**Response 200**: Array of Table objects with column metadata.

#### POST /v1/schemas

**Purpose**: Create or update schema (upsert).

**Request**:
```json
{
  "database_id": "db_001",
  "name": "public",
  "tables": [
    {
      "name": "customers",
      "description": "Customer master data",
      "columns": [
        {
          "name": "id",
          "ordinal_position": 1,
          "data_type": "uuid",
          "is_nullable": false,
          "is_primary_key": true,
          "default_value": "gen_random_uuid()"
        }
      ],
      "ddl": "CREATE TABLE customers (id UUID PRIMARY KEY, ...)"
    }
  ],
  "relationships": [
    {
      "source_table_name": "customers",
      "source_column": "id",
      "target_table_name": "orders",
      "target_column": "customer_id",
      "relationship_type": "foreign_key",
      "confidence": 1.0
    }
  ]
}
```

**Response 201**: Created schema with IDs.

#### GET /v1/schemas/{schema_id}/changes

**Purpose**: Get schema version diff since last sync.

**Response 200**:
```json
{
  "schema_id": "sch_001",
  "current_version": 5,
  "previous_version": 4,
  "changes": [
    { "type": "table_added", "name": "audit_log", "at": "2026-07-08T14:00:00Z" },
    { "type": "column_added", "table": "customers", "column": "tax_id", "at": "2026-07-09T10:00:00Z" },
    { "type": "column_removed", "table": "customers", "column": "old_field", "at": "2026-07-09T10:00:00Z" }
  ]
}
```

#### GET /v1/tables/{table_id}

**Purpose**: Get single table with full column details.

#### GET /v1/tables/{table_id}/columns

**Purpose**: Get columns for a table.

#### GET /v1/relationships

**Query Parameters**: `?table_id=tbl_001`

**Purpose**: Get relationships for a table or all relationships for a tenant.

#### POST /v1/relationships

**Purpose**: Create a relationship (manual or inferred).

#### DELETE /v1/relationships/{relationship_id}

**Purpose**: Delete a relationship.

---

### 7.3 Vector Index

#### POST /v1/vectors/search

**Purpose**: Hybrid search across all embedded content for a tenant.

**Request**:
```json
{
  "query_vector": [0.012, -0.034, ...],
  "query_text": "customer revenue",
  "filter": {
    "content_type": { "in": ["schema_element", "business_term"] },
    "source": { "eq": "connector" }
  },
  "top_k": 20,
  "score_threshold": 0.5,
  "hybrid_alpha": 0.75
}
```

**Validation**:
| Field | Rule |
|-------|------|
| query_vector | Required if query_text not provided, array of 1024 floats |
| query_text | Required if query_vector not provided, min 3 chars |
| filter | Optional, Qdrant filter syntax |
| top_k | Optional, 1-100, default 20 |
| score_threshold | Optional, 0.0-1.0, default 0.0 |
| hybrid_alpha | Optional, 0.0 (BM25 only) - 1.0 (vector only), default 0.75 |

**Response 200**:
```json
{
  "results": [
    {
      "id": "vec_001",
      "score": 0.89,
      "payload": {
        "content_type": "schema_element",
        "source_id": "tbl_001",
        "text": "customers: Customer master data with contact information and account details"
      }
    }
  ],
  "meta": {
    "total": 15,
    "took_ms": 45
  }
}
```

#### POST /v1/vectors/upsert

**Purpose**: Upsert vectors into the tenant's Qdrant collection.

**Request**:
```json
{
  "points": [
    {
      "id": "vec_001",
      "vector": [0.012, -0.034, ...],
      "payload": {
        "content_type": "schema_element",
        "source_id": "tbl_001",
        "tenant_id": "tnt_001",
        "text": "customers: customer master data"
      }
    }
  ]
}
```

**Response 200**:
```json
{
  "status": "ok",
  "data": { "upserted_count": 1 }
}
```

#### POST /v1/vectors/batch

**Purpose**: Batch upsert (up to 1000 points).

Same as upsert but array of points can be up to 1000.

#### DELETE /v1/vectors/{vector_id}

**Purpose**: Delete a single vector point.

---

### 7.4 Graph Store

#### POST /v1/graph/nodes

**Purpose**: Create a graph node.

**Request**:
```json
{
  "node_type": "table",
  "external_id": "tbl_001",
  "label": "customers",
  "properties": {
    "description": "Customer master data",
    "domain": "sales"
  }
}
```

**Response 201**:
```json
{
  "id": "gnode_001",
  "node_type": "table",
  "label": "customers"
}
```

#### POST /v1/graph/edges

**Purpose**: Create a graph edge.

**Request**:
```json
{
  "source_node_id": "gnode_001",
  "target_node_id": "gnode_002",
  "edge_type": "references",
  "weight": 1.0,
  "properties": {
    "source_column": "customer_id",
    "target_column": "id"
  }
}
```

#### GET /v1/graph/traverse

**Purpose**: Traverse graph from a start node.

**Query Parameters**: `?node_id=gnode_001&edge_types=references,frequently_joined&max_depth=3`

**Response 200**:
```json
{
  "paths": [
    {
      "nodes": [
        { "id": "gnode_001", "label": "customers", "node_type": "table" },
        { "id": "gnode_002", "label": "orders", "node_type": "table" },
        { "id": "gnode_003", "label": "order_items", "node_type": "table" }
      ],
      "edges": [
        { "source": "gnode_001", "target": "gnode_002", "type": "references" },
        { "source": "gnode_002", "target": "gnode_003", "type": "references" }
      ],
      "total_weight": 2.0
    }
  ]
}
```

#### GET /v1/graph/search

**Purpose**: Search nodes by label or property.

**Query Parameters**: `?q=customer&node_type=table,domain`

---

### 7.5 History Store

#### POST /v1/history

**Purpose**: Log a query execution.

**Request**:
```json
{
  "user_id": "usr_001",
  "database_id": "db_001",
  "natural_query": "Show revenue by customer",
  "generated_sql": "SELECT ...",
  "executed_sql": "SELECT ...",
  "status": "success",
  "result_summary": { "row_count": 42, "columns": ["name", "total_revenue"] },
  "execution_time_ms": 2340,
  "total_time_ms": 3450,
  "model_used": "qwen2.5-72b",
  "cost": 0.0024,
  "policy_results": [ ... ]
}
```

#### GET /v1/history

**Purpose**: Query history with filters.

**Query Parameters**: `?user_id=usr_001&status=success&limit=50&offset=0&from=2026-07-01&to=2026-07-10`

#### POST /v1/history/search

**Purpose**: Full-text search across natural_query and generated_sql.

**Request**:
```json
{
  "query": "revenue by customer",
  "limit": 50,
  "filters": { "status": "success" }
}
```

---

### 7.6 Feedback Store

#### POST /v1/feedback

**Purpose**: Store user feedback.

**Request**:
```json
{
  "query_id": "qry_001",
  "user_id": "usr_001",
  "rating": "negative",
  "corrected_sql": "SELECT ...",
  "comment": "Wrong date filter",
  "category": "wrong_filter"
}
```

#### GET /v1/feedback/pending

**Purpose**: Get unprocessed feedback (for learning loop).

**Response 200**:
```json
{
  "items": [
    {
      "id": "fb_001",
      "query_id": "qry_001",
      "rating": "negative",
      "corrected_sql": "SELECT ..."
    }
  ],
  "total": 42
}
```

#### PUT /v1/feedback/{feedback_id}/process

**Purpose**: Mark feedback as processed (by learning loop).

**Request**:
```json
{
  "processed": true,
  "quality_score": 0.85
}
```

---

### 7.7 Config Store

#### GET /v1/config

**Query Parameters**: `?scope=tenant&scope_id=tnt_001`

**Response 200**:
```json
{
  "configs": [
    { "key": "default_model_tier", "value": "auto" },
    { "key": "max_rows_per_query", "value": 1000 }
  ]
}
```

#### PUT /v1/config

**Request**:
```json
{
  "scope": "tenant",
  "scope_id": "tnt_001",
  "key": "default_model_tier",
  "value": "medium"
}
```

---

### 7.8 Metrics Store

#### POST /v1/metrics

**Purpose**: Record a metric datapoint.

**Request**:
```json
{
  "metric_name": "pipeline.query.latency_ms",
  "value": 2340,
  "tags": {
    "tenant_id": "tnt_001",
    "model": "qwen2.5-72b",
    "status": "success"
  },
  "recorded_at": "2026-07-10T10:00:00Z"
}
```

#### GET /v1/metrics/aggregate

**Query Parameters**: `?metric_name=pipeline.query.latency_ms&aggregate=p95&from=2026-07-01&to=2026-07-10&group_by=model`

**Response 200**:
```json
{
  "results": [
    { "group": { "model": "sqlcoder-7b-2" }, "value": 1200 },
    { "group": { "model": "qwen2.5-72b" }, "value": 3400 }
  ]
}
```

---

### 7.9 Audit Store

#### POST /v1/audit

**Purpose**: Log an audit event.

**Request**:
```json
{
  "user_id": "usr_001",
  "action": "query_executed",
  "resource_type": "query",
  "resource_id": "qry_001",
  "details": {
    "database_id": "db_001",
    "policy_result": "passed",
    "sql_hash": "sha256_abc123"
  },
  "ip_address": "203.0.113.42",
  "user_agent": "OpenCode CLI v1.0"
}
```

#### GET /v1/audit

**Query Parameters**: `?user_id=usr_001&action=query_executed&from=2026-07-01&to=2026-07-10&page=1&page_size=50`

---

## 8. Agent APIs (Internal)

Agent APIs are implemented as LangGraph nodes within the query-pipeline service. They communicate via the shared `QueryState` object, not HTTP.

### 8.1 Intent Agent

**Contract**: `IntentAgent.process(state: QueryState) -> QueryState`

**Input** (from QueryState):
```json
{
  "query_id": "qry_001",
  "natural_query": "Show me total revenue by customer for last quarter",
  "metadata": {
    "tenant_id": "tnt_001",
    "database_id": "db_001",
    "model_tier_hint": "auto"
  }
}
```

**Output** (adds to QueryState):
```json
{
  "intent": {
    "type": "aggregate",
    "domain": "sales",
    "sub_domain": "revenue",
    "confidence": 0.95,
    "entities": [
      { "text": "revenue", "type": "metric", "normalized": "total" },
      { "text": "customer", "type": "dimension" },
      { "text": "last quarter", "type": "time_filter", "normalized": "2026-Q2" }
    ],
    "complexity": "medium"
  },
  "model_tier": "qwen2.5-72b"
}
```

**Failure mode**: If confidence < 0.6, set state.error = ERR-014 and return to orchestrator.

**Performance**: P50 < 100ms, P95 < 200ms

### 8.2 Retriever Agent

**Contract**: `RetrieverAgent.process(state: QueryState) -> QueryState`

**Input**: QueryState with intent populated, raw query text.

**Output** (adds to QueryState):
```json
{
  "context": {
    "tables": [ ... ],
    "columns": [ ... ],
    "relationships": [ ... ],
    "business_terms": [ ... ],
    "query_patterns": [ ... ],
    "stats": {
      "total_candidates": 85,
      "after_dedup": 42,
      "after_truncation": 18,
      "tokens_used": 6120,
      "retrieval_time_ms": 185
    }
  }
}
```

**Failure mode**: If no relevant tables found, set state.warnings and continue with empty context.

**Performance**: P50 < 200ms, P95 < 400ms

### 8.3 Planner Agent

**Contract**: `PlannerAgent.process(state: QueryState) -> QueryState`

**Input**: QueryState with intent + context.

**Output** (adds to QueryState):
```json
{
  "plan": {
    "plan_id": "plan_001",
    "feasible": true,
    "tables_required": ["customers", "orders"],
    "join_path": [ ... ],
    "filters": [ ... ],
    "aggregations": [ ... ],
    "group_by": ["customers.name"],
    "order_by": [ ... ],
    "limit": 100,
    "model_tier": "qwen2.5-72b",
    "warnings": [],
    "estimated_complexity": 0.6
  }
}
```

**Failure mode**: If plan is infeasible, set state.error = ERR-015.

**Performance**: P50 < 400ms, P95 < 800ms

### 8.4 Generator Agent

**Contract**: `GeneratorAgent.process(state: QueryState) -> QueryState`

**Input**: QueryState with intent + context + plan.

**Output** (adds to QueryState):
```json
{
  "sql_candidates": [
    {
      "sql": "SELECT c.name, SUM(o.total) ...",
      "model": "qwen2.5-72b",
      "confidence": 0.87,
      "tokens_in": 2840,
      "tokens_out": 312,
      "cost": 0.0022,
      "generation_time_ms": 1100
    }
  ],
  "selected_sql": "SELECT c.name, SUM(o.total) ...",
  "selected_candidate_index": 0
}
```

**Failure mode**: If all models fail, set state.error = ERR-016.

**Performance**: Simple: P50 < 800ms. Medium: P50 < 1.5s. Complex: P50 < 3s.

### 8.5 Validator Agent

**Contract**: `ValidatorAgent.process(state: QueryState) -> QueryState`

**Input**: QueryState with selected_sql.

**Output** (adds to QueryState):
```json
{
  "validation": {
    "valid": true,
    "syntax_valid": true,
    "schema_valid": true,
    "aggregate_valid": true,
    "filter_logic_valid": true,
    "errors": [],
    "warnings": []
  }
}
```

**Failure mode**: If validation fails, set state.validation.valid = false and set state.needs_repair = true.

**Performance**: P50 < 100ms, P95 < 200ms

### 8.6 Repair Agent

**Contract**: `RepairAgent.process(state: QueryState) -> QueryState`

**Input**: QueryState with validation errors.

**Output**: Updated state with repaired SQL and repair count incremented.

**Max iterations**: 2. After 2nd failure, set state.error.

**Performance**: P50 < 300ms, P95 < 500ms

### 8.7 Policy Enforcement Agent

**Contract**: `PolicyEnforcementAgent.process(state: QueryState) -> QueryState`

**Input**: QueryState with validated SQL.

**Output** (adds to QueryState):
```json
{
  "policy_results": [
    { "layer": "intent_classification", "passed": true, "ms": 15 },
    { "layer": "sql_sanitization", "passed": true, "ms": 5 },
    { "layer": "rbac", "passed": true, "ms": 10 },
    { "layer": "cost_ceiling", "passed": true, "estimated_rows": 150, "ms": 8 },
    { "layer": "sql_validation", "passed": true, "ms": 25 },
    { "layer": "read_only", "passed": true, "ms": 3 },
    { "layer": "audit_logging", "already_logged": true, "ms": 24 },
    { "layer": "data_classification", "passed": true, "pii_detected": false, "ms": 20 },
    { "layer": "advanced_validation", "passed": true, "ms": 15 },
    { "layer": "anomaly_detection", "passed": true, "anomaly_score": 0.02, "ms": 30 }
  ],
  "policy_passed": true
}
```

**Failure mode**: If any layer fails, set state.policy_passed = false, state.error = ERR-012.

**Performance**: P50 < 150ms, P95 < 300ms

### 8.8 Executor Agent

**Contract**: `ExecutorAgent.process(state: QueryState) -> QueryState`

**Input**: QueryState with validated SQL and passed policy enforcement.

**Output** (adds to QueryState):
```json
{
  "execution": {
    "results": [ ... ],
    "columns": [ ... ],
    "row_count": 42,
    "truncated": false,
    "execution_time_ms": 430,
    "db_version": "PostgreSQL 16.3"
  }
}
```

**Failure mode**: On DB error, set state.error = ERR-009 (unreachable) or ERR-010 (timeout).

**Performance**: DB-dependent. Target: P50 < 200ms, P95 < 2s.

---

## 9. Event API (Internal, Async)

Events are published via Redis Pub/Sub or a message broker. All event schemas are versioned with `event_type` and `event_version` fields.

### 9.1 Event Envelope

```json
{
  "event_id": "evt_001",
  "event_type": "query.completed",
  "event_version": 1,
  "source": "query-pipeline",
  "timestamp": "2026-07-10T10:00:00Z",
  "tenant_id": "tnt_001",
  "correlation_id": "qry_001",
  "data": {}
}
```

### 9.2 Event Catalog

| Event Type | Version | Source | Consumers | Description |
|-----------|---------|--------|-----------|-------------|
| `query.submitted` | 1 | public-api | query-pipeline | New query submitted |
| `query.completed` | 1 | query-pipeline | learning-loop, public-api | Query finished (success/fail) |
| `query.feedback_received` | 1 | public-api | learning-loop | User feedback submitted |
| `schema.sync_completed` | 1 | schema-intelligence | ke-api, learning-loop | Schema sync finished |
| `schema.sync_failed` | 1 | schema-intelligence | ke-api | Schema sync failed |
| `schema.change_detected` | 1 | schema-intelligence | ke-api | Schema change found |
| `learning.cycle_completed` | 1 | learning-loop | ke-api | Learning batch cycle done |
| `tenant.provisioned` | 1 | admin | ke-api, schema-intelligence | New tenant ready |
| `tenant.deleted` | 1 | admin | all | Tenant deleted, cleanup |
| `model.deployed` | 1 | infra | query-pipeline | New model version deployed |

### 9.3 Event Schemas

#### query.completed (v1)
```json
{
  "event_type": "query.completed",
  "event_version": 1,
  "data": {
    "query_id": "qry_001",
    "tenant_id": "tnt_001",
    "user_id": "usr_001",
    "database_id": "db_001",
    "status": "success",
    "execution_time_ms": 2340,
    "cost": 0.0024,
    "model_used": "qwen2.5-72b",
    "row_count": 42,
    "feedback_token": "fb_token_abc"
  }
}
```

#### schema.sync_completed (v1)
```json
{
  "event_type": "schema.sync_completed",
  "event_version": 1,
  "data": {
    "database_id": "db_001",
    "tenant_id": "tnt_001",
    "tables_synced": 142,
    "columns_synced": 2840,
    "relationships_found": 85,
    "duration_ms": 45000,
    "changes_detected": 3
  }
}
```

---

## 10. WebSocket API

### 10.1 Connection

**Endpoint**: `wss://api.opencode.ai/ws/v1/query`

**Auth**: JWT in query string: `wss://api.opencode.ai/ws/v1/query?token=eyJhbG...`

**Connection lifecycle**:
1. Client connects with JWT token
2. Server validates JWT, extracts tenant_id and user_id
3. Server sends `connection_ack` message
4. Client sends subscribe/query messages
5. Server streams results
6. Either party closes

### 10.2 Message Format

**Client -> Server**:
```json
{
  "type": "query.submit",
  "payload": {
    "query": "Show revenue by customer",
    "database_id": "db_001",
    "options": {
      "model_tier": "auto"
    }
  },
  "id": "msg_001"
}
```

**Server -> Client** (progress updates):
```json
{
  "type": "query.progress",
  "payload": {
    "query_id": "qry_001",
    "stage": "generating",
    "progress": 0.6,
    "message": "Generating SQL with Qwen2.5-72B..."
  },
  "id": "msg_001"
}
```

**Server -> Client** (policy enforcement warning):
```json
{
  "type": "policy.warning",
  "payload": {
    "query_id": "qry_001",
    "guard": "cost_ceiling",
    "message": "This query may scan approximately 500,000 rows. Consider adding filters.",
    "action_required": false
  },
  "id": "msg_001"
}
```

**Server -> Client** (final result):
```json
{
  "type": "query.result",
  "payload": {
    "query_id": "qry_001",
    "status": "success",
    "sql": "SELECT ...",
    "results": [ ... ],
    "columns": [ ... ],
    "row_count": 42,
    "execution_ms": 2340,
    "cost": 0.0024
  },
  "id": "msg_001"
}
```

### 10.3 Error Handling

```json
{
  "type": "error",
  "payload": {
    "code": "ERR-012",
    "message": "Policy enforcement blocked query: unauthorized table access"
  },
  "id": "msg_001"
}
```

---

## 11. Streaming API

### 11.1 SSE Endpoint

**Endpoint**: `GET /v1/stream/query/{query_id}`

**Headers**: `Authorization: Bearer <token>`, `Accept: text/event-stream`

**Purpose**: Stream query execution progress and results as Server-Sent Events.

### 11.2 Event Stream

```
event: progress
data: {"query_id":"qry_001","stage":"intent","progress":0.1,"message":"Analyzing query intent..."}

event: progress
data: {"query_id":"qry_001","stage":"retrieval","progress":0.2,"message":"Retrieving schema context..."}

event: progress
data: {"query_id":"qry_001","stage":"planning","progress":0.3,"message":"Building query plan..."}

event: progress
data: {"query_id":"qry_001","stage":"generation","progress":0.5,"message":"Generating SQL..."}

event: sql_generated
data: {"query_id":"qry_001","sql":"SELECT c.name, SUM(o.total) ...","model":"qwen2.5-72b"}

event: progress
data: {"query_id":"qry_001","stage":"validation","progress":0.7,"message":"Validating SQL..."}

event: progress
data: {"query_id":"qry_001","stage":"execution","progress":0.9,"message":"Executing against database..."}

event: result
data: {"query_id":"qry_001","status":"success","row_count":42,"columns":[...],"results":[...],"execution_ms":2340,"cost":0.0024}

event: done
data: {"query_id":"qry_001","status":"success"}
```

---

## 12. Error Catalog

| Code | HTTP | Name | Description | Recovery |
|------|------|------|-------------|----------|
| ERR-001 | 500 | INTERNAL_ERROR | Unexpected server error | Retry with exponential backoff (3x max). If persists, contact support. |
| ERR-002 | 503 | SERVICE_UNAVAILABLE | Dependency unavailable (DB, Qdrant, model) | Retry with backoff (5s, 15s, 30s). Notify if all retries fail. |
| ERR-003 | 429 | RATE_LIMITED | Too many requests | Wait for `Retry-After` header duration (seconds). |
| ERR-004 | 401 | UNAUTHORIZED | Missing or invalid authentication | Re-authenticate. If API key, check key is active. |
| ERR-005 | 403 | FORBIDDEN | Authenticated but no permission | Contact tenant admin for role upgrade. |
| ERR-006 | 404 | NOT_FOUND | Resource not found | Verify resource ID. Resources are tenant-scoped — check tenant context. |
| ERR-007 | 400 | VALIDATION_ERROR | Request body failed validation | Fix fields listed in `details.fields`. |
| ERR-008 | 403 | TENANT_MISMATCH | X-Tenant-Id doesn't match JWT tenant | Correct `X-Tenant-Id` header. |
| ERR-009 | 503 | DB_UNREACHABLE | Target database connection failed | Check database credentials, network access, and if DB is running. 3 retry attempts. |
| ERR-010 | 408 | QUERY_TIMEOUT | Query exceeded timeout limit | Simplify query or increase `options.timeout_seconds`. |
| ERR-011 | 400 | QUERY_TOO_COSTLY | Query exceeds cost ceiling | Add filters, limit scope, or contact admin to increase ceiling. |
| ERR-012 | 400 | UNSAFE_QUERY | Policy enforcement blocked the query | Check `details.policy_results` for which layer failed. Modify query accordingly. |
| ERR-013 | 404 | SCHEMA_NOT_FOUND | Database schema not yet synced | Trigger schema sync via `POST /v1/databases/{id}/sync`. |
| ERR-014 | 400 | INVALID_INTENT | Could not classify query intent | Rephrase query to be more specific. Include table names or business terms. |
| ERR-015 | 400 | PLAN_INFEASIBLE | Query plan cannot be constructed | Query may reference tables or columns that don't exist in the schema. |
| ERR-016 | 503 | MODEL_TIMEOUT | LLM inference timed out | Retry. If persists, model may be overloaded — degrade to simpler model. |
| ERR-017 | 503 | MODEL_UNAVAILABLE | Inference model not loaded or unavailable | Switch model tier or retry later. |
| ERR-018 | 400 | FEEDBACK_INVALID | Malformed or invalid feedback | Check `details.fields` for errors. |
| ERR-019 | 409 | CONFLICT | Resource conflict (duplicate, concurrent edit) | Retry with different Idempotency-Key. |
| ERR-020 | 400 | JOB_FAILED | Async job completed with failure | Check `data.job_result.error` for details. Retry job. |
| ERR-021 | 400 | QUERY_CANCELLED | Query was cancelled by user | Submit new query if needed. |
| ERR-022 | 422 | UNPROCESSABLE_ENTITY | Request body valid but semantically incorrect | Check `details` for semantic validation errors. |
| ERR-023 | 502 | BAD_GATEWAY | Upstream service returned error | Retry. Downstream service may be recovering. |
| ERR-024 | 504 | GATEWAY_TIMEOUT | Upstream service timed out | Retry with backoff. |
| ERR-025 | 413 | PAYLOAD_TOO_LARGE | Request body exceeds size limits | Reduce payload size. Max request: 1MB. Max query: 4000 chars. |
| KE-001 | 404 | STORE_NOT_FOUND | KE store entity not found | Verify UUID. |
| KE-002 | 400 | TENANT_REQUIRED | X-Tenant-Id missing on tenant-scoped endpoint | Add header. |
| KE-003 | 401 | INVALID_SERVICE_TOKEN | X-Service-Token missing or invalid | Check service token configuration. |
| KE-004 | 500 | STORE_OPERATION_FAILED | KE store internal operation failed | Retry. If persists, check store health. |
| KE-005 | 503 | QDRANT_CONNECTION_FAILED | Qdrant cluster unreachable | Retry. Check Qdrant cluster health. |
| KE-006 | 503 | DATABASE_CONNECTION_FAILED | PostgreSQL connection failed | Retry. Check PG cluster health. |

---

## 13. Rate Limiting

### 13.1 By Plan Tier

| Tier | Requests/min | Burst | Cost cap/day | Concurrent queries |
|------|-------------|-------|-------------|-------------------|
| Free | 10 | 5 | $0.10 | 1 |
| Starter | 100 | 20 | $1.00 | 3 |
| Pro | 500 | 100 | $5.00 | 10 |
| Enterprise | Custom | Custom | Custom | Custom |

### 13.2 By Endpoint

| Endpoint | Rate | Notes |
|----------|------|-------|
| POST /v1/auth/login | 5/min per IP | Brute force protection |
| POST /v1/query | Plan-dependent | Most heavily rate-limited |
| GET /v1/query/{id} | 60/min | Polling protection |
| GET /v1/databases/{id}/schemas | 30/min | Schema reading |
| POST /v1/feedback | 30/min | Feedback submission |
| POST /v1/databases | 5/min | Database connection changes |
| POST /v1/databases/{id}/sync | 1/5min | Sync frequency protection |
| GET /v1/admin/* | 30/min | Admin operations |

### 13.3 Rate Limit Headers

Every response includes:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1628528400
Retry-After: 8  (only on 429 responses)
```

---

## 14. Multi-Tenancy

### 14.1 Tenant Identification

**Header**: `X-Tenant-Id: tnt_001`

**Propagation flow**:
1. Public API extracts `X-Tenant-Id` from request (or from JWT claim)
2. Public API passes to internal services via gRPC metadata or HTTP header
3. KE API validates tenant_id matches service token's authorized tenants
4. KE API sets PostgreSQL session variable: `SET app.tenant_id = 'tnt_001'`
5. RLS policies filter all queries automatically

### 14.2 Tenant-Aware Endpoints

| API | Tenant Header | Notes |
|-----|---------------|-------|
| POST /v1/auth/login | Not required | Returns tenant_id in response |
| POST /v1/query | Required | Queries execute within tenant scope |
| GET /v1/databases | Required | Returns tenant's databases only |
| KE API (all) | Required | RLS applies to all store operations |
| POST /v1/admin/team/invite | Required | Invites within tenant scope |

### 14.3 Cross-Tenant Access

- Explicitly forbidden at every layer
- Public API middleware validates JWT tenant_id matches X-Tenant-Id
- KE API RLS ensures no cross-tenant data leakage
- Audit logged for any attempted cross-tenant access (even if rejected)

---

## 15. Idempotency

### 15.1 Supported Operations

| Operation | Idempotency Key Behavior |
|-----------|------------------------|
| POST /v1/query | Same key within 24h returns cached result. Key not consumed if query still processing (409). |
| POST /v1/feedback | Same key within 24h returns cached response. Prevents duplicate feedback. |
| POST /v1/databases | Same key within 24h returns cached response. Prevents duplicate connections. |
| POST /v1/databases/{id}/sync | Same key within 5min returns "already syncing". |

### 15.2 Implementation

1. Client generates UUID v4 as Idempotency-Key
2. Server checks if key exists in cache (Redis, TTL 24h)
3. If exists and completed -> return cached response
4. If exists and processing -> return 409 Conflict
5. If not exists -> process request, cache response with key
6. Cache includes: request body hash, response body, status code, timestamp

---

## 16. Retry Behavior

### 16.1 Client Retry Guidelines

| Error Code | Retryable | Strategy |
|-----------|-----------|----------|
| ERR-001 (500) | Yes | Exponential backoff: 1s, 2s, 4s, max 3 retries |
| ERR-002 (503) | Yes | Exponential backoff: 5s, 15s, 30s, max 3 retries |
| ERR-003 (429) | Yes | Respect Retry-After header |
| ERR-009 (503) | Yes | Exponential backoff: 5s, 15s, 30s, max 3 retries |
| ERR-016 (503) | Yes | Exponential backoff: 2s, 5s, 10s, max 3 retries |
| ERR-017 (503) | Yes | Exponential backoff: 2s, 5s, 10s, max 3 retries |
| ERR-023 (502) | Yes | Exponential backoff: 1s, 2s, 4s, max 3 retries |
| ERR-024 (504) | Yes | Exponential backoff: 1s, 2s, 4s, max 3 retries |
| ERR-004 (401) | No | Retry won't help (re-authenticate) |
| ERR-005 (403) | No | Retry won't help (permission issue) |
| ERR-006 (404) | No | Resource doesn't exist |
| ERR-007 (400) | No | Fix request body |
| ERR-010 (408) | No | Query is too complex |

### 16.2 Server-Side Retry

| Service | Retry On | Strategy |
|---------|----------|----------|
| Query Pipeline | KE API failure | Retry KE API call 3x with 100ms backoff |
| Query Pipeline | Target DB failure | Return error to user (ERR-009), do NOT auto-retry user's query |
| Schema Intel | Target DB failure | Retry connection 3x with 5s, 15s, 30s backoff |
| Schema Intel | KE API write failure | Retry KE API call 3x with 500ms, 1s, 2s backoff |
| Learning Loop | KE API write failure | Retry 3x with 1s, 2s, 4s backoff. If still fails, log and skip batch |
| Learning Loop | DB query failure | Skip batch, retry on next cycle |

---

## 17. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1.0 | 2026-07-10 | Chief API Architect | Initial draft — all endpoints defined |
| 1.0.0 | TBD | — | First approved version |

---

## 18. Future Compatibility

### 18.1 Extension Points

| Area | Planned Evolution | Backward Compat? |
|------|------------------|-----------------|
| Query endpoint | Add streaming mode (SSE) for real-time results | Yes (new option field) |
| Query options | Add `explain` mode for query explanation | Yes (new option field) |
| Schema endpoint | Add `relationships` sub-resource | Yes (new sub-path) |
| Admin endpoints | Add `usage/export` for CSV export | Yes (new endpoint) |
| Auth | Add OAuth2/OIDC support | Yes (new grant type) |
| API | Add gRPC for high-throughput internal calls | Yes (parallel to REST) |
| Models | Add new model tiers | Yes (new enum value) |
| Agent APIs | Add new agents (e.g., explanation agent) | Yes (new LangGraph nodes) |

### 18.2 Deprecation Policy

1. **Announce**: Deprecated features announced on API changelog and via `Sunset` header
2. **Timeline**: 6 months minimum support after deprecation announcement
3. **Migration**: Migration guide provided for all breaking changes
4. **Metrics**: Deprecated endpoint usage monitored; proactive migration outreach for heavy users

### 18.3 Schema Evolution Rules

- Never remove fields from existing responses
- New fields are optional in both request and response
- Enum values are additive only (never remove)
- Error codes are never removed, only deprecated
- Pagination format is frozen (will not change)
