# Schema Specification

**Enterprise Data Intelligence Platform — Schema Intelligence Subsystem**

| Metadata | Value |
|----------|-------|
| **Author** | Principal Data Platform Architect |
| **Date** | 2026-07-10 |
| **Status** | Approved |
| **Version** | 1.0 |
| **Architecture Reference** | System-Architecture.md \u00a73.1, Component-Design.md \u00a73 |
| **Cross-References** | KnowledgeEngine-Specification.md \u00a72-3, Database-Specification.md \u00a75, AI-Agent-Specification.md \u00a72-3, API-Specification.md \u00a76.4-6.5, Performance-Specification.md \u00a71, \u00a74, \u00a76 |

---

## 1. Goals & Responsibilities

### 1.1 Mission

Make every database schema \u2014 no matter how poorly documented \u2014 understandable to both machines and humans by autonomously discovering metadata, inferring relationships, detecting business meaning, and maintaining a living semantic model that improves over time.

### 1.2 Primary Goals

| Goal | Target | Measured By |
|------|--------|-------------|
| Autonomous schema discovery | 100% of accessible schemas | Discovery coverage metric |
| Primary key detection accuracy | > 95% | Validated against known PKs in test datasets |
| Foreign key inference precision | > 85% | Precision@K against human-annotated relationships |
| Business entity detection recall | > 80% | Recall against curated business ontology |
| Column description generation | > 70% rated helpful | Human rating (1-5 scale) |
| Full sync for 200-table schema | < 5 minutes | Timer from trigger to KE write |
| Incremental sync for 10 tables | < 30 seconds | Timer from trigger to KE write |
| Cold start to usable state | < 30 minutes | Time to first queryable schema |

### 1.3 Responsibilities

| Responsibility | Description | Owner |
|---------------|-------------|-------|
| Metadata extraction | Introspect database catalogs, extract tables, columns, types, constraints | Connector module |
| Schema enrichment | Generate descriptions, detect business entities, infer semantics | Annotator module |
| Relationship inference | Discover PK/FK relationships, join paths, cross-DB links | Inferer module |
| Embedding generation | Create vector embeddings for schema elements | Embedder module |
| Change detection | Detect schema changes, trigger re-sync | Change Detector |
| Version management | Track schema versions, support rollback | Version Manager |
| Confidence scoring | Assign confidence scores to all inferred metadata | Scorer module |

### 1.4 Non-Responsibilities

| Not Responsible For | Handled By |
|--------------------|------------|
| Query execution | Query Executor (EP-011) |
| Context retrieval for NL2SQL | Context Retriever (EP-007) |
| Feedback collection | Feedback Collector / Learning Loop (EP-012) |
| Business glossary management | Knowledge Graph (KE \u00a76) |
| Database connection management | Tenant configuration (KE \u00a79) |

---

## 2. Supported Database Types

### 2.1 Tier 1: Full Support (MVP)

| Database | Connector | Dialect | Introspection Method | Limitations |
|----------|-----------|---------|---------------------|-------------|
| PostgreSQL | PostgresConnector | PostgreSQL | information_schema + pg_catalog | None |
| MySQL | MySQLConnector | MySQL | information_schema | No partial indexes |
| Microsoft SQL Server | MSSQLConnector | MSSQL | INFORMATION_SCHEMA + sys.* | No cross-DB foreign keys |
| BigQuery | BigQueryConnector | BigQuery | INFORMATION_SCHEMA | No primary keys |
| Snowflake | SnowflakeConnector | Snowflake | INFORMATION_SCHEMA | Limited constraint info |

### 2.2 Tier 2: Query-Only (Post-MVP)

| Database | Connector | Dialect | Introspection Method | ETA |
|----------|-----------|---------|---------------------|-----|
| Oracle | OracleConnector | Oracle | ALL_TAB_COLUMNS + ALL_CONSTRAINTS | Month 3 |
| SQLite | SQLiteConnector | SQLite | sqlite_master + PRAGMA table_info | Month 2 |
| Redshift | RedshiftConnector | Redshift | pg_catalog (subset) | Month 3 |
| CockroachDB | CRDBConnector | PostgreSQL | information_schema | Month 4 |
| YugabyteDB | YugabyteConnector | PostgreSQL | information_schema | Month 4 |

### 2.3 Tier 3: Future

| Database | Rationale |
|----------|-----------|
| MongoDB | Document-based; requires schema inference from documents |
| DynamoDB | NoSQL; requires table scan inference |
| Cassandra | Wide-column; limited metadata |
| ClickHouse | Columnar; limited constraint support |

### 2.4 Connector Interface

```python
class Connector(ABC):
    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> None:
        ...
    @abstractmethod
    async def fetch_databases(self) -> list[DatabaseInfo]:
        ...
    @abstractmethod
    async def fetch_tables(self, database: str, schema: str | None = None) -> list[TableInfo]:
        ...
    @abstractmethod
    async def fetch_columns(self, database: str, schema: str | None, table: str) -> list[ColumnInfo]:
        ...
    @abstractmethod
    async def fetch_primary_keys(self, database: str, schema: str | None, table: str) -> list[str]:
        ...
    @abstractmethod
    async def fetch_foreign_keys(self, database: str, schema: str | None, table: str) -> list[ForeignKeyInfo]:
        ...
    @abstractmethod
    async def fetch_indexes(self, database: str, schema: str | None, table: str) -> list[IndexInfo]:
        ...
    @abstractmethod
    async def fetch_row_count(self, database: str, schema: str | None, table: str) -> int | None:
        ...
    @abstractmethod
    async def fetch_sample_data(self, database: str, schema: str | None, table: str, limit: int = 100) -> list[dict] | None:
        ...
    @abstractmethod
    async def test_connection(self, config: ConnectionConfig) -> ConnectionTestResult:
        ...
    @abstractmethod
    async def close(self) -> None:
        ...
```

---

## 3. Metadata Extraction Pipeline

### 3.1 Pipeline Overview

```
User Request          Extraction              Processing              Storage
--sync database-->   +--------------+    +---------------+    +----------------+
                     | Connector    |--->| DDL Parser    |--->| Schema Store   |
                     | (DB-specific)|    | (normalize)   |    | (PostgreSQL)   |
                     +--------------+    +------+--------+    +----------------+
                                              |
                     +--------------+         |
                     | PK Discovery  |-------->|
                     +--------------+         |
                     +--------------+         v
                     | FK Discovery  |    +---------------+    +----------------+
                     +--------------+--->| Annotator     |--->| Vector Index   |
                                          | (LLM)         |    | (Qdrant)       |
                     +--------------+    +------+--------+    +----------------+
                     | Relationship  |           |
                     | Inference    |---------->|
                     +--------------+           |
                     +--------------+           v
                     | Profiling    |    +---------------+    +----------------+
                     | (Sample Data)|--->| Embedder      |--->| Knowledge Graph|
                     +--------------+    | (BGE-M3)      |    | (PostgreSQL)   |
                                          +---------------+    +----------------+
```

### 3.2 Pipeline Stages

| Stage | Component | Input | Output | Latency Budget |
|-------|-----------|-------|--------|---------------|
| 1 | Connector | Connection config | Raw metadata (DDL, columns, constraints) | DB-dependent |
| 2 | DDL Parser | Raw metadata | Normalized schema objects | < 5s per 100 tables |
| 3 | PK Discovery | Column metadata | PK candidates with confidence | < 2s per 100 tables |
| 4 | FK Discovery | Column metadata + PK results | FK candidates with confidence | < 5s per 100 tables |
| 5 | Relationship Inference | PK/FK + naming + history | Inferred relationships | < 10s per 100 tables |
| 6 | Column Profiling | Sample data (100 rows) | Data type hints, null %, distinct %, min/max | < 30s per 100 tables |
| 7 | Annotator (LLM) | All extracted metadata | Descriptions, business entities, semantic types | < 2 min per 100 tables |
| 8 | Embedder (BGE-M3) | Metadata + descriptions | Vector embeddings (1024-d dense + sparse) | < 10s per 100 tables |
| 9 | Store Writer | All enriched metadata | Write to KE stores | < 5s per 100 tables |

### 3.3 Stage Retry Logic

| Stage | Max Retries | Backoff | Fallback |
|-------|-------------|---------|----------|
| Connector connection | 3 | Exponential (1s, 4s, 15s) | Report connection failure |
| DDL Parser | 2 | Linear (1s, 2s) | Use raw metadata |
| PK/FK Discovery | 1 | None | Confidence = 0, human review flag |
| Relationship Inference | 1 | None | Generate for high-confidence pairs only |
| Column Profiling | 2 | Exponential (1s, 4s) | Use type info only |
| Annotator (LLM) | 3 | Exponential (5s, 20s, 60s) | Use *UNKNOWN* convention, queue for batch |
| Embedder (BGE-M3) | 2 | Exponential (1s, 4s) | Defer to next sync cycle |
| Store Writer | 3 | Exponential (1s, 5s, 25s) | Log error, alert if persistent |

### 3.4 Parallel Execution Model

```
Extraction Workers (configurable pool size: 4-16)
    +-- Worker 1: Fetch databases
    +-- Worker 2: Fetch tables (parallelized per database)
    +-- Worker 3: Fetch columns + PKs (parallelized per table)
    +-- Worker 4: Fetch FKs + indexes (parallelized per table)

Processing Workers (configurable pool size: 2-8)
    +-- Worker 5: Parse DDL + normalize
    +-- Worker 6: Profile columns (sample data)

ML Workers (configurable pool size: 1-4)
    +-- Worker 7: Annotate (LLM batch)
    +-- Worker 8: Embed (BGE-M3 batch)
```

---

## 4. Primary Key Discovery

### 4.1 Discovery Methods (Priority Order)

| Method | Source | Reliability | When Used |
|--------|--------|------------|-----------|
| **M1: Explicit PK constraint** | information_schema.TABLE_CONSTRAINTS | 100% | Available for most relational DBs |
| **M2: Unique index on non-null column** | Index metadata + nullability | 95% | When PK constraint absent but unique index exists |
| **M3: Single-column unique pattern** | Column named id, _id, <table>_id, pk_* | 85% | When no constraints or unique indexes |
| **M4: Multi-column unique pattern** | Composite naming (order_id, product_id in same table) | 70% | When no explicit PK (junction tables) |
| **M5: Heuristic inference** | Column with highest distinct count + not-null + identity-named | 60% | No constraints, no naming clues |

### 4.2 Confidence Scoring

```python
def score_pk_confidence(method: int, column: ColumnInfo, table: TableInfo) -> float:
    base = {1: 1.0, 2: 0.95, 3: 0.85, 4: 0.70, 5: 0.60}[method]
    if column.nullable:
        base *= 0.5
    if column.is_composite_type:
        base *= 0.7
    if column.default_value and "nextval" in (column.default_value or "").lower():
        base = min(base + 0.1, 1.0)
    return round(base, 2)
```

### 4.3 Acceptance Criteria

- [ ] All explicit PK constraints discovered with 100% accuracy
- [ ] PK names stored in columns.is_primary_key field
- [ ] Composite PKs supported (multiple columns flagged)
- [ ] Confidence score stored per PK inference
- [ ] No false positives for tables without PKs (M5 may still fire \u2014 flag as low confidence)
- [ ] PK discovery completes before FK discovery (FK depends on PK)

---

## 5. Foreign Key Discovery

### 5.1 Discovery Methods (Priority Order)

| Method | Source | Reliability | When Used |
|--------|--------|------------|-----------|
| **M1: Explicit FK constraint** | information_schema.REFERENTIAL_CONSTRAINTS | 100% | Available for most relational DBs |
| **M2: Named pattern match** | Column named <referenced_table>_id or <referenced_table>_key | 90% | When no explicit FK constraint exists |
| **M3: Type + name + cardinality** | Same data type + name similarity + sample data match | 75% | When M1 and M2 fail |
| **M4: Query history mining** | Common join patterns in executed queries | 80% | Post-MVP, requires query history accumulation |

### 5.2 FK Inference Algorithm

```python
async def infer_foreign_keys(columns, tables, existing_fks, sample_data):
    candidates = []
    candidates.extend(m1_explicit_constraints(existing_fks))
    for col in columns:
        for tbl in tables:
            match = m2_name_pattern(col, tbl)
            if match:
                candidates.append(match)
    unmatched = [c for c in columns if not any_fk_match(c, candidates)]
    for col in unmatched:
        for tbl in tables:
            match = await m3_type_cardinality_match(col, tbl, sample_data)
            if match and match.confidence >= 0.6:
                candidates.append(match)
    return deduplicate_and_rank(candidates)
```

### 5.3 Acceptance Criteria

- [ ] All explicit FK constraints discovered with 100% accuracy
- [ ] Named pattern matching (M2) achieves > 90% precision on test datasets
- [ ] Type + cardinality matching (M3) achieves > 75% precision
- [ ] Self-referencing FKs detected
- [ ] Composite FKs supported (multi-column)
- [ ] Cross-schema FKs detected (when same DB)
- [ ] Cross-database FKs flagged as low confidence (requires human review)
- [ ] FK confidence scores stored in relationships.confidence

---

## 6. Relationship Inference

### 6.1 Relationship Types

| Type | Description | Example | Confidence Range |
|------|-------------|---------|-----------------|
| **PK-FK Direct** | Column references PK of another table | orders.customer_id \u2192 customers.id | 0.9 - 1.0 |
| **PK-FK Indirect** | Column references non-PK unique column | orders.order_code \u2192 order_codes.code | 0.6 - 0.9 |
| **Lookup** | Small table referenced by many tables | status_codes.id \u2192 orders.status | 0.7 - 0.9 |
| **Junction** | Composite PK table joining two entities | order_products(order_id, product_id) | 0.8 - 1.0 |
| **Self-Reference** | Column references PK of same table | employees.manager_id \u2192 employees.id | 0.9 - 1.0 |
| **Inheritance** | Table PK references another table's PK (1:1) | users.id \u2192 profiles.id | 0.5 - 0.7 |
| **Cross-Database** | Likely FK across databases | sales_db.orders.customer_id \u2192 crm_db.customers.id | 0.3 - 0.6 |
| **Naming Clue** | Name similarity suggests relationship | order_total in orders might relate to total_amount | 0.3 - 0.5 |

### 6.2 Graph Building

After relationship inference, results are written to the Knowledge Graph graph_nodes and graph_edges tables (see Database-Specification.md \u00a76):

### 6.3 Join Path Discovery

```python
async def discover_join_paths(graph, start_tables, max_depth=5, min_confidence=0.7):
    paths = []
    for start in start_tables:
        visited = set()
        queue = [(start, [])]
        while queue:
            current, path = queue.pop(0)
            if len(path) >= max_depth:
                continue
            for edge in graph.get_outgoing_edges(current.id):
                if edge.confidence < min_confidence:
                    continue
                if edge.target_table_id in visited:
                    continue
                new_path = path + [edge]
                paths.append(JoinPath(
                    tables=[start.id] + [e.target_table_id for e in new_path],
                    edges=new_path,
                    total_confidence=product(e.confidence for e in new_path),
                ))
                queue.append((edge.target_table, new_path))
                visited.add(edge.target_table_id)
    return sorted(paths, key=lambda p: p.total_confidence, reverse=True)
```

### 6.4 Acceptance Criteria

- [ ] All explicit FK-FK relationships discovered
- [ ] Inferred relationships stored with confidence scores
- [ ] Cross-database relationships flagged for human review
- [ ] Join paths up to depth 5 discoverable
- [ ] Relationship graph queryable via KE API within 50ms P95
- [ ] Junction tables correctly identified (composite PKs with only FK columns)

---

## 7. Column Profiling

### 7.1 Profiling Operations

| Profile | Method | Output | Cost |
|---------|--------|--------|------|
| Null ratio | COUNT(*) WHERE col IS NULL | 0.0 - 1.0 | Full table scan (heavy) |
| Distinct ratio | COUNT(DISTINCT col) | 0.0 - 1.0 | Full table scan (heavy) |
| Min/Max values | MIN(col), MAX(col) | Range endpoints | Full table scan (heavy) |
| Sample distinct values | SELECT DISTINCT col LIMIT 100 | Sample values | Index scan |
| Data type detection | Examine sample values | Refined type hint | Light |
| Length statistics (string) | MIN(LENGTH), MAX(LENGTH), AVG(LENGTH) | Length range | Full scan (heavy) |
| Numeric distribution | Histogram buckets on sample | Distribution shape | Light (sample based) |
| Common patterns (string) | Regex detection on samples | Format pattern | Light (sample based) |
| Foreign key match ratio | Sample FK values exist in referenced table | Match % | Light (sampled) |

### 7.2 Performance Optimization

```
Profiling Mode           Cost          Accuracy
-----------------------------------------------
Fast (default)           < 5s/table    ~90%
Standard                 < 30s/table   ~95%
Full (explicit opt-in)   < 5min/table  ~100%
```

Fast mode: Sample 1000 rows (or 1% of table, whichever is smaller).
Standard mode: Sample 10000 rows (or 5% of table).
Full mode: Full table scan (user-initiated, rate-limited).

### 7.3 Type Refinement

```python
def refine_column_type(col, sample_values):
    non_null = [v for v in sample_values if v is not None]
    if not non_null:
        return SemanticType.UNKNOWN
    if all(is_date(v) for v in non_null[:50]):
        return SemanticType.DATETIME if any(has_time_component(v) for v in non_null[:50]) else SemanticType.DATE
    if all(is_email(v) for v in non_null[:50]):
        return SemanticType.EMAIL
    if all(is_url(v) for v in non_null[:50]):
        return SemanticType.URL
    if all(is_phone(v) for v in non_null[:50]):
        return SemanticType.PHONE
    if all(is_ip(v) for v in non_null[:50]):
        return SemanticType.IP_ADDRESS
    return SemanticType.from_declared(col.data_type)
```

### 7.4 Acceptance Criteria

- [ ] Fast profiling completes within 5s per table for tables under 1M rows
- [ ] Null ratio and distinct ratio available for all profiled columns
- [ ] Sample distinct values available for string columns
- [ ] Type refinement detects: date, datetime, email, URL, phone, IP
- [ ] Profiling does not cause query timeouts on source databases
- [ ] Profiling results stored and queryable via KE API

---

## 8. Business Entity Detection

### 8.1 Entity Catalog

| Entity | Detection Pattern | Priority Columns | Confidence |
|--------|------------------|-----------------|------------|
| **Customer** | customer, client, member, buyer | customer_id, email, name, phone | 0.9 |
| **Product** | product, item, sku, goods | product_id, sku, name, price, category | 0.9 |
| **Order** | order, purchase, transaction, invoice | order_id, customer_id, total, status, date | 0.9 |
| **Employee** | employee, staff, worker, personnel | employee_id, email, name, department, manager_id | 0.9 |
| **Invoice** | invoice, bill, receipt, charge | invoice_id, customer_id, amount, date, due_date | 0.85 |
| **Payment** | payment, charge, settlement, remittance | payment_id, invoice_id, amount, method, date | 0.85 |
| **Address** | address, location, place, site | address_id, street, city, state, zip, country | 0.85 |
| **Category** | category, type, class, group, segment | category_id, name, parent_category_id | 0.8 |
| **User** | user, account, login, profile | user_id, email, username, role, status | 0.85 |
| **Department** | department, division, unit, team, org | department_id, name, manager_id, budget | 0.8 |
| **Inventory** | inventory, stock, warehouse, bin | product_id, quantity, location, warehouse_id | 0.8 |
| **Shipment** | shipment, delivery, dispatch, fulfillment | shipment_id, order_id, status, tracking, date | 0.8 |
| **Subscription** | subscription, plan, membership, tier | subscription_id, customer_id, plan, status, start_date | 0.8 |
| **Transaction** | transaction, ledger, entry, journal | transaction_id, account_id, amount, type, date | 0.8 |

### 8.2 Custom Entity Detection (LLM)

For entities not in the predefined catalog, use LLM-based detection with a prompt analyzing table name, column names, data types, row count, and relationships. The LLM returns a JSON response with is_entity, entity_type, confidence, identifier_column, and reasoning.

### 8.3 Acceptance Criteria

- [ ] All predefined entities detected with \u2265 80% recall on test datasets
- [ ] Custom entity detection provides confidence scores
- [ ] Entity types stored in tables.business_entity field
- [ ] Entities exposed through KE API resolve endpoint
- [ ] False positive rate < 10% for entity detection

---

## 9. Semantic Type Detection

### 9.1 Semantic Type Hierarchy

```
SemanticType
+-- IDENTIFIER
|   +-- UUID
|   +-- SEQUENCE (auto-increment integer)
|   +-- NATURAL_KEY (business key, e.g., SSN, ISBN)
+-- TEXT
|   +-- NAME (person name, company name)
|   +-- DESCRIPTION (long-form text)
|   +-- CODE (short code: status, category)
|   +-- EMAIL
|   +-- URL
|   +-- PHONE
|   +-- ADDRESS (street-level)
|   +-- JSON (structured text)
+-- NUMERIC
|   +-- INTEGER
|   |   +-- COUNT (inventory, quantity)
|   |   +-- RANK (priority, score)
|   |   +-- YEAR
|   +-- DECIMAL
|       +-- PRICE (monetary amount)
|       +-- RATIO (percentage, rate)
|       +-- COORDINATE (lat/lng)
+-- TEMPORAL
|   +-- DATE, DATETIME, TIMESTAMP, TIME, INTERVAL
+-- BOOLEAN
|   +-- FLAG (is_active, is_deleted)
|   +-- STATUS (binary status)
+-- BINARY
    +-- BLOB
    +-- FILE_REFERENCE
```

### 9.2 Detection Strategy

| Level | Method | Confidence | Examples |
|-------|--------|------------|---------|
| **L1: Declared type** | SQL data type mapping | 0.5 - 1.0 | VARCHAR \u2192 TEXT; INTEGER \u2192 NUMERIC |
| **L2: Column name** | Regex on column name | 0.6 - 0.95 | created_at \u2192 TEMPORAL.DATETIME |
| **L3: Sample data** | Value pattern matching | 0.7 - 0.95 | Values match phone pattern \u2192 TEXT.PHONE |
| **L4: FK target** | Referenced table semantic type | 0.5 - 0.8 | product_id FK \u2192 IDENTIFIER |
| **L5: LLM analysis** | LLM on column + context | 0.6 - 0.9 | Ambiguous columns with business context |

### 9.3 Acceptance Criteria

- [ ] Level 1-2 detection covers 90% of columns
- [ ] Level 3 value-pattern detection accuracy > 95% for: email, URL, phone, date
- [ ] LLM analysis (Level 5) only invoked for < 10% of columns (the ambiguous ones)
- [ ] Semantic types stored in columns.semantic_type field
- [ ] Types queryable through KE API

---

## 10. Synonym Generation

### 10.1 Synonym Types

| Synonym Type | Example | Source |
|-------------|---------|--------|
| **Column alias** | cust_id \u2192 customer_id, customer_identifier | LLM generation |
| **Business term** | revenue \u2192 sales_amount, total_revenue, gross_sales | LLM + glossary |
| **Abbreviation** | qty \u2192 quantity, amt \u2192 amount, dept \u2192 department | Rule-based + LLM |
| **Acronym** | sku \u2192 stock_keeping_unit, eod \u2192 end_of_day | LLM explanation |
| **Cross-language** | cliente (Spanish) \u2192 customer | LLM translation |
| **Historical name** | old_cust_id \u2192 customer_id (renamed column) | Query history mining |

### 10.2 Generation Pipeline

Synonyms generated via LLM prompt analyzing column name, table, data type, and sample values. Rule-based abbreviations also generated for common patterns. Results deduplicated and ranked by confidence.

### 10.3 Storage

Synonyms stored in two places:
1. **Vector Index (Qdrant)**: Each synonym is a separate indexed entry linked to the original column for semantic search.
2. **Knowledge Graph**: Synonyms stored as node properties on column nodes for graph traversal.

### 10.4 Acceptance Criteria

- [ ] Each column generates 3-10 synonyms on average
- [ ] Synonym generation covers: abbreviations, business terms, alternative phrasings
- [ ] Synonyms indexed in Qdrant for semantic search
- [ ] Synonym quality rated > 70% helpful in human evaluation
- [ ] No offensive synonyms generated (content filter in prompt)

---

## 11. Business Glossary Integration

### 11.1 Glossary Import

Supports import from:
- CSV files (term, definition, owner, domain)
- Alation Data Catalog API
- Collibra Data Intelligence Cloud
- DataBook semantic layer

### 11.2 Term-to-Column Matching

```python
async def match_glossary_terms(glossary_terms, schema_columns, vector_client):
    matches = []
    for term in glossary_terms:
        term_embedding = await embedder.embed(f"{term.name}: {term.description}")
        results = await vector_client.search(
            collection_name="schema_columns",
            query_vector=term_embedding,
            limit=5,
            score_threshold=0.65,
        )
        for result in results:
            matches.append(TermMatch(term_id=term.id, column_id=result.id,
                similarity_score=result.score, match_method="vector_similarity",
                confidence=calculate_match_confidence(result.score, term, result.column)))
    return matches
```

### 11.3 Glossary-Driven Enrichment

When a glossary term matches a column, the column inherits: business description, owner, domain/category, definition URL, and related terms.

### 11.4 Acceptance Criteria

- [ ] Glossary import from CSV works (MVP)
- [ ] Glossary import from Alation/Collibra/DataBook (post-MVP)
- [ ] Term-to-column matching achieves > 80% precision
- [ ] Matched terms stored as columns.glossary_term_id and in knowledge graph
- [ ] Glossary terms indexed in Qdrant for semantic discovery
- [ ] Conflicting term mappings flagged for human review

---

## 12. Confidence Scoring

### 12.1 Scoring Model

Every piece of inferred metadata carries a confidence score (0.0 - 1.0):

| Metadata Type | Range | Auto-Accept Threshold | Human Review Threshold |
|---------------|-------|----------------------|----------------------|
| Primary key (M1 explicit) | 1.0 | \u2265 0.9 | N/A |
| Primary key (M2-M5 inferred) | 0.6 - 0.95 | \u2265 0.85 | < 0.85 |
| Foreign key (M1 explicit) | 1.0 | \u2265 0.9 | N/A |
| Foreign key (M2-M3 inferred) | 0.6 - 0.9 | \u2265 0.80 | < 0.80 |
| Relationship inference | 0.3 - 1.0 | \u2265 0.75 | < 0.75 |
| Column description (LLM) | 0.5 - 0.95 | \u2265 0.70 | < 0.70 |
| Business entity | 0.6 - 0.95 | \u2265 0.80 | < 0.80 |
| Semantic type | 0.5 - 1.0 | \u2265 0.80 | < 0.80 |
| Synonym | 0.5 - 0.95 | \u2265 0.70 | < 0.70 |
| Profile statistics | 0.9 - 1.0 | \u2265 0.90 | N/A (statistical) |
| Business glossary match | 0.5 - 0.95 | \u2265 0.80 | < 0.80 |

### 12.2 Confidence Factors

```python
def calculate_confidence(base_confidence, factors):
    score = base_confidence
    for factor in factors:
        if factor.type == FactorType.CONSISTENCY:
            score += factor.value * 0.1
        elif factor.type == FactorType.CHECKSUM:
            score += factor.value * 0.05
        elif factor.type == FactorType.SAMPLE:
            score += factor.value * 0.1
        elif factor.type == FactorType.GLOSSARY:
            score += factor.value * 0.15
        elif factor.type == FactorType.HISTORY:
            score += factor.value * 0.1
        elif factor.type == FactorType.CONFLICT:
            score -= factor.value * 0.2
    return min(max(score, 0.0), 1.0)
```

### 12.3 Acceptance Criteria

- [ ] Every inferred metadata element has a confidence score
- [ ] Scores stored and queryable through KE API
- [ ] Thresholds configurable per tenant
- [ ] Human review overrides stored with reviewer identity and timestamp
- [ ] Confidence scores updated when new evidence available (re-sync, feedback)

---

## 13. Schema Versioning

### 13.1 Version Model

```sql
CREATE TABLE schema_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    database_id UUID NOT NULL REFERENCES databases(id),
    version INTEGER NOT NULL,
    snapshot JSONB NOT NULL,
    checksum TEXT NOT NULL,
    change_summary JSONB,
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL DEFAULT 'system',
    status TEXT NOT NULL DEFAULT 'active',
    metadata JSONB
);
CREATE INDEX idx_schema_versions_active ON schema_versions(database_id, version DESC) WHERE status = 'active';
```

### 13.2 Version Lifecycle

```
Sync Trigger \u2192 Snapshot Current \u2192 Compare with Previous \u2192 Changes Detected?
                                                              +-- No \u2192 No new version
                                                              +-- Yes \u2192 Create new version
                                                                       +-- Update status of old to superseded
                                                                       +-- Store change summary
                                                                       +-- Notify subscribers

Rollback Request \u2192 Fetch target version \u2192 Re-instate columns \2192 Create rollback version
                                                              +-- status = rollback
                                                              +-- Re-embed modified elements
```

### 13.3 Change Summary Format

```json
{
    "added_tables": ["new_table_2024"],
    "removed_tables": ["obsolete_table"],
    "modified_tables": [{"table": "orders", "added_columns": ["discount_pct"], "removed_columns": ["old_discount"]}],
    "added_relationships": [{"source": "orders.customer_id", "target": "customers.id", "confidence": 1.0}],
    "schema_impact": "minor"
}
```

### 13.4 Version Retention

| Tenants | Versions Retained | Reason |
|---------|------------------|--------|
| < 10 | All versions | Debugging, rollback capability |
| 10 - 100 | 50 most recent | Storage optimization |
| 100 - 1K | 25 most recent | Storage optimization |
| > 1K | 10 most recent + monthly snapshots | Aggressive optimization |

### 13.5 Acceptance Criteria

- [ ] Schema changes detected on every sync cycle
- [ ] New version created only when changes detected (no-op syncs don't create versions)
- [ ] Version history queryable through KE API
- [ ] Rollback to any retained version supported
- [ ] Change summary provides human-readable diff
- [ ] Version checksum enables integrity verification

---

## 14. Incremental Schema Refresh

### 14.1 Trigger Sources

| Trigger | Method | Latency | Frequency |
|---------|--------|---------|-----------|
| **Scheduled** | Cron job per database | 5-60 min | Configurable per tenant |
| **Webhook** | Database event notification | < 1 min | On schema change |
| **Manual** | User clicks Sync Now in UI | Immediate | On demand |
| **Change detected** | Periodic checksum comparison | < 5 min | Every 5 min for active DBs |
| **Query failure** | FK/table not found in query execution | Immediate | On query error |

### 14.2 Incremental vs Full Sync

| Aspect | Full Sync | Incremental Sync |
|--------|-----------|-----------------|
| Scope | All objects | Changed objects only |
| Duration | 5 min (200 tables) | < 30s (10 tables) |
| Impact on KE | Full re-embed | Partial re-embed |
| When to use | First sync, manual trigger, schema version gap > 30 days | Scheduled, webhook, periodic |
| Locking | Read lock on KE stores | No locks |

### 14.3 Incremental Detection Algorithm

```python
async def detect_incremental_changes(database_id, connector, previous_snapshot):
    changes = SchemaDiff()
    current_tables = await connector.fetch_tables(database_id)
    previous_tables = previous_snapshot.tables
    changes.added_tables = current_tables - previous_tables
    changes.removed_tables = previous_tables - current_tables
    common_tables = current_tables & previous_tables
    for table in common_tables:
        current_columns = await connector.fetch_columns(database_id, table)
        previous_columns = previous_snapshot.columns[table]
        if column_set_hash(current_columns) != column_set_hash(previous_columns):
            changes.modified_tables.append(TableDiff(name=table,
                added_columns=current_columns - previous_columns,
                removed_columns=previous_columns - current_columns))
    current_fks = await connector.fetch_foreign_keys(database_id)
    previous_fks = previous_snapshot.foreign_keys
    changes.added_fks = current_fks - previous_fks
    changes.removed_fks = previous_fks - current_fks
    return changes
```

### 14.4 Acceptance Criteria

- [ ] Incremental sync completes in < 30 seconds for < 10 changed tables
- [ ] No unnecessary re-embedding of unchanged elements
- [ ] Webhook trigger latency < 1 second from database event
- [ ] Scheduled sync interval configurable per database (5 min - 24 hours)
- [ ] Manual sync does not interrupt ongoing queries

---

## 15. Change Detection

### 15.1 Detection Methods

| Method | What It Detects | Reliability | Cost |
|--------|----------------|-------------|------|
| **Checksum comparison** | Any schema change | 100% | Full table list scan |
| **information_schema polling** | Column adds/removes/type changes | 100% | Per-table query |
| **DDL trigger (PostgreSQL)** | Real-time DDL events | 100% | Requires trigger setup |
| **Query failure analysis** | Backward-incompatible changes | Reactive | Zero cost (passive) |

### 15.2 Change Categories

| Category | Example | Impact | Auto-Remediate |
|----------|---------|--------|---------------|
| **Column added** | New column in table | Low | Yes \u2014 embed new column |
| **Column removed** | Column dropped | High | Yes \u2014 mark as deprecated |
| **Column renamed** | cust_id \u2192 customer_id | High | Detect via FK + type match |
| **Column type changed** | INT \u2192 BIGINT | Medium | Yes \u2014 update type |
| **Table added** | New table in schema | Low | Yes \u2014 run full pipeline |
| **Table removed** | Table dropped | High | Yes \u2014 mark as deprecated |
| **Table renamed** | cust \u2192 customers | High | Detect via FK + content match |
| **Index added/removed** | Performance change | Low | Log only |
| **FK constraint added** | New relationship | Medium | Yes \u2014 add to graph |
| **FK constraint removed** | Relationship dropped | Medium | Yes \u2014 remove from graph |

### 15.3 Change Notification

```python
# Event published to event bus on schema change
event = {
    "event_type": "schema.change_detected",
    "payload": {
        "database_id": "db_001",
        "change_summary": {...},
        "severity": "high",
        "requires_re_embed": True,
        "notify_tenant": True,
    },
    "metadata": {"trace_id": "trace_abc123", "timestamp": "2026-07-10T14:30:00Z"},
}
```

### 15.4 Acceptance Criteria

- [ ] All schema changes detected within one sync cycle
- [ ] Column rename detected with > 80% accuracy (via FK + type + position matching)
- [ ] Table rename detected with > 70% accuracy (via FK + column overlap)
- [ ] Changes categorized by severity (low, medium, high)
- [ ] Critical changes (column removed, table dropped) trigger immediate notification
- [ ] False positive rate for change detection < 5%

---

## 16. Large Schema Handling (10K+ Tables)

### 16.1 Challenges

| Challenge | Impact | Mitigation |
|-----------|--------|------------|
| Full sync time (10K tables) | Could exceed 4 hours | Parallel extraction, streaming writes |
| Memory pressure (10K table metadata) | > 2GB RAM per sync | Stream processing, batch writes |
| LLM annotation cost (10K tables x 10 columns) | > 100K API calls | Batch annotation, tiered processing |
| Embedding storage (10K tables x 10 columns) | > 1M vectors | Partitioned Qdrant collections |
| Graph visualization | Unreadable | Hierarchical clustering, search-first UI |

### 16.2 Tiered Processing Strategy

| Tier | Table Count | Processing Level | Annotations | Profiling | ETA |
|------|-------------|-----------------|-------------|-----------|-----|
| Active | Top 20% by query frequency | Full | Yes (LLM) | Full | 30 min |
| Recent | Top 50% by recency | Standard | Yes (LLM batch) | Standard | 1 hour |
| Rest | Remaining 50% | Minimal | No (rule-based only) | Fast | 2 hours |
| Archive | Unused for 90+ days | None | None (metadata only) | None | \u2014 |

### 16.3 Parallel Extraction Configuration

```
For schemas > 1,000 tables:
  Parallelism: 8 workers
  Batch size: 50 tables per worker
  Stream writes: 100 records per batch
  Memory limit: 500MB per worker
  Timeout per table: 30 seconds

For schemas > 5,000 tables:
  Parallelism: 16 workers
  Batch size: 25 tables per worker
  Stream writes: 50 records per batch
  Memory limit: 250MB per worker
  Use cursor-based pagination for table listing
```

### 16.4 Acceptance Criteria

- [ ] 10K-table schema fully synced within 4 hours
- [ ] Active tier (top 20%) annotated within 30 minutes
- [ ] Memory consumption < 4GB during large schema sync
- [ ] Qdrant collection handles 1M+ vectors with < 100ms P95 query latency
- [ ] UI gracefully handles 10K table listing (virtual scrolling, search-first)
- [ ] No database timeouts on source systems during large schema sync

---

## 17. Multi-Tenant Isolation

### 17.1 Isolation Model

Shared Schema Intelligence workers write to tenant-scoped KE stores. tenant_id in every row + per-tenant Qdrant collection.

### 17.2 Isolation Boundaries

| Resource | Isolation Mechanism | Scope |
|----------|-------------------|-------|
| Database connections | Per-tenant connection pool | Separate TCP connections |
| Extraction metadata | tenant_id column in every table | Row-level in shared schema store |
| Vector index | Per-tenant Qdrant collection | Collection-level |
| Knowledge graph | tenant_id on graph nodes/edges | Row-level in shared PG |
| Configuration | tenant_id in config store | Row-level |
| Processing | Tenant-aware worker pool | Separate task queues |
| Rate limits | Per-tenant extraction rates | Configurable QPS |
| Credentials | Kubernetes secrets per tenant | Namespace-scoped |

### 17.3 Tenant Rate Limiting

```python
EXTRACTION_RATE_LIMITS = {
    "free":   {"max_tables_per_sync": 100,  "max_qpm": 10,  "max_concurrent": 1,  "profiling": False, "llm": False},
    "starter":{"max_tables_per_sync": 500,  "max_qpm": 30, "max_concurrent": 2,  "profiling": True,  "llm": True, "quality": "fast"},
    "pro":    {"max_tables_per_sync": 2000, "max_qpm": 100,"max_concurrent": 4,  "profiling": True,  "llm": True, "quality": "standard"},
    "enterprise":{"max_tables_per_sync": 10000, "max_qpm": -1, "max_concurrent": 8, "profiling": True, "llm": True, "quality": "full"},
}
```

### 17.4 Acceptance Criteria

- [ ] Tenant A's schema extraction does not affect Tenant B's in-flight queries
- [ ] Per-tenant rate limits enforced during extraction
- [ ] Credentials stored and accessed per-tenant only
- [ ] No cross-tenant data leakage in schema store queries
- [ ] Tenant can delete all schema data on account deletion (GDPR compliance)

---

## 18. APIs

### 18.1 Internal Schema Intelligence API (Port 8300, Internal)

| Endpoint | Method | Description |
|----------|--------|-------------|
| /v1/sync/start | POST | Trigger a full or incremental schema sync |
| /v1/sync/status/{job_id} | GET | Get sync job status |
| /v1/sync/{job_id}/cancel | POST | Cancel an in-progress sync |
| /v1/sync/schedule | PUT | Configure sync schedule |
| /v1/sync/detect | POST | Detect changes without syncing |
| /v1/annotate/column | POST | Annotate a single column |
| /v1/annotate/batch | POST | Batch annotate columns |
| /v1/profile | POST | Profile a table |
| /v1/entities/detect | POST | Detect business entities |
| /v1/glossary/import | POST | Import glossary terms |
| /v1/glossary/match | POST | Match glossary terms to columns |
| /v1/versions/{database_id} | GET | List schema versions |
| /v1/versions/{database_id}/{version} | GET | Get specific schema version |
| /v1/versions/{database_id}/rollback/{version} | POST | Rollback to previous version |
| /v1/health | GET | Health check |

### 18.2 Event API

| Event | Emitter | Subscribers |
|-------|---------|-------------|
| schema.sync.started | SI API | Status dashboard |
| schema.sync.completed | SI API | KE, Learning Loop |
| schema.sync.failed | SI API | Alerting, status |
| schema.change.detected | Change Detector | KE, Frontend |
| schema.version.created | Version Manager | Audit, KE |
| schema.version.rollback | Version Manager | Audit, KE |
| schema.annotation.ready | Annotator | Embedder |
| schema.embedding.ready | Embedder | KE (index refresh) |

### 18.3 Integration with KE API

Schema Intelligence data consumed through KE API endpoints:
- POST /v1/ke/schema/resolve \u2192 Schema store + annotations
- POST /v1/ke/retrieve \u2192 Vector index (with schema embeddings)
- GET /v1/ke/schema/databases \u2192 Schema store
- GET /v1/ke/schema/table/{id} \u2192 Schema store + annotations
- POST /v1/ke/schema/sync \u2192 Triggers Schema Intelligence sync

---

## 19. Storage Model

### 19.1 Schema Store (PostgreSQL)

Tables defined in Database-Specification.md \u00a75: tenants, databases, schema_infos, tables, columns, relationships.

### 19.2 Vector Index (Qdrant)

Three per-tenant Qdrant collections:
| Collection | Content | Vector Dim |
|------------|---------|------------|
| {tenant_id}_schema_columns | Column name + description + synonym embeddings | 1024-d + sparse |
| {tenant_id}_schema_tables | Table name + entity type embeddings | 1024-d + sparse |
| {tenant_id}_schema_synonyms | Synonym embeddings mapped to columns | 1024-d + sparse |

### 19.3 Knowledge Graph (PostgreSQL)

Schema relationships stored in graph_nodes and graph_edges tables. Edge types: foreign_key, inferred_fk, lookup, junction, belongs_to_entity, has_synonym, maps_to_glossary_term.

### 19.4 Cache (Redis)

| Cache Key | TTL | Invalidated By |
|-----------|-----|---------------|
| si:{tenant}:schema:{db_hash} | 60s | Schema change event |
| si:{tenant}:db_list | 300s | Database add/remove |
| si:{tenant}:annotations:{col_id} | 3600s | Re-annotation |
| si:{tenant}:profile:{table_id} | 1800s | Re-profiling |

---

## 20. Failure Modes

### 20.1 Failure Catalog

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| **Database unreachable** | Connector timeout | Retry 3x with backoff, report error |
| **Permission denied** | Error in introspection query | Report specific missing permissions |
| **Timeout during extraction** | Sync job > 30 min | Split into smaller batches, resume |
| **LLM API failure** | HTTP error from LLM | Fallback to *UNKNOWN*, queue for retry |
| **LLM hallucination** | Feedback flagging | Use *UNKNOWN* for low confidence |
| **Embedding service down** | Embedder health check | Skip embedding, mark as pending |
| **Schema change mid-sync** | Checksum mismatch | Abort, restart full re-sync |
| **Storage full** | Disk usage monitor | Pause extraction, alert on-call |
| **Cross-tenant data leak** | Audit check in store writer | Reject write, security incident |
| **Large schema memory OOM** | Process exit / OOMKill | Reduce batch size, stream writes |

### 20.2 Degraded Mode Behavior

| Degraded State | Behavior | User Impact |
|----------------|----------|-------------|
| LLM annotation offline | Use rule-based descriptions only | Less helpful descriptions |
| Embedding service offline | Skip new embeddings, serve cached | No semantic search for new columns |
| Profiling unavailable | Skip profiling, use type-only info | Less accurate type detection |
| Connector pool exhausted | Queue sync requests | Sync delayed |
| Qdrant read-only | Use PostgreSQL fallback (BM25 only) | No vector similarity search |
| PostgreSQL read-only | Cache-only mode | Stale cache, no schema changes |

### 20.3 Acceptance Criteria

- [ ] Every failure mode has documented detection and recovery
- [ ] No single failure prevents usability (degraded mode always available)
- [ ] Failures logged with trace context
- [ ] Critical failures alert on-call engineer

---

## 21. Performance Targets

### 21.1 Latency Budgets

| Operation | P50 | P95 | P99 |
|-----------|-----|-----|-----|
| Full sync (200 tables) | 3 min | 5 min | 8 min |
| Incremental sync (10 tables) | 15s | 30s | 60s |
| Inline annotation (single column) | 2s | 5s | 10s |
| Batch annotation (100 columns) | 30s | 60s | 120s |
| Column profiling (fast mode) | 2s | 5s | 10s |
| PK discovery (100 tables) | 2s | 5s | 10s |
| FK inference (100 tables) | 5s | 15s | 30s |
| Relationship inference (100 tables) | 10s | 30s | 60s |
| Embedding generation (100 items) | 5s | 10s | 20s |
| Change detection | 5s | 15s | 30s |
| Glossary import (1K terms) | 10s | 20s | 40s |
| Schema version creation | 2s | 5s | 10s |

### 21.2 Throughput Targets

| Metric | Target |
|--------|--------|
| Concurrent extractions (tenant) | 4 per pool worker |
| Tables extracted per minute | 200 |
| Columns annotated per minute | 100 (batch LLM) |
| Vectors indexed per minute | 500 |
| Glossary terms matched per minute | 500 |
| Max tables per daily sync (single DB) | 10,000 |

### 21.3 Resource Budgets

| Resource | Per Extraction Worker | Per Pool | Burst |
|----------|----------------------|----------|-------|
| CPU | 1 core | 4-16 cores | 32 cores |
| Memory | 500MB | 8GB | 16GB |
| Network | 10 Mbps | 100 Mbps | 500 Mbps |
| DB connections | 5 per worker | 80 | 160 |
| LLM requests/min | 30 (batch) | 120 | 300 |

### 21.4 Acceptance Criteria

- [ ] P50 latency targets met under normal load
- [ ] P95 latency targets met under 2x expected load
- [ ] Throughput targets sustained for 30+ minute sync operations
- [ ] No OOM errors under expected load

---

## 22. Security Considerations

### 22.1 Threat Model

| Threat | Vector | Mitigation |
|--------|--------|------------|
| **T-01: Credential leak** | Connection config stored in KE config store | Encrypt at rest (AES-256), audit access |
| **T-02: SQL injection via introspection** | Malicious database name in DDL | Parameterized queries, never interpolate |
| **T-03: LLM prompt injection** | Malicious column/table names | Sanitize input to LLM, strip SQL |
| **T-04: Cross-tenant data access** | Missing tenant_id filter | tenant_id enforced in every query |
| **T-05: Data exfiltration via sample data** | Sample data contains PII | Min/max only for PII columns, masking |
| **T-06: DoS via large schema** | Intentional 10K table schema | Per-tenant rate limits, pool bounds |
| **T-07: Man-in-the-middle** | Unencrypted DB connection | TLS required for all connections |
| **T-08: Insecure storage of sample data** | Sample data retained indefinitely | TTL on sample data (7 days), GDPR |

### 22.2 Data Classification

| Data Class | Storage | Encryption | Retention |
|------------|---------|------------|-----------|
| Schema metadata | PostgreSQL + Qdrant | AES-256 at rest | Tenant lifecycle |
| Connection credentials | K8s Secrets + Vault | AES-256 + envelope | Tenant lifecycle |
| Sample data | Temporary Redis cache | AES-256 in transit | 7 days max |
| LLM prompts | In-memory (not stored) | TLS in transit | Not stored |
| LLM responses | PostgreSQL | AES-256 at rest | Tenant lifecycle |
| Audit logs | Audit store (immutable) | SHA-256 linked | 7 years |

### 22.3 Acceptance Criteria

- [ ] All database connections use TLS
- [ ] Connection credentials never logged or stored in plaintext
- [ ] Sample data TTL enforced (auto-delete after 7 days)
- [ ] Sample data excluded for PII columns
- [ ] Tenant isolation verified by integration test
- [ ] Audit log captures all schema intelligence operations

---

## 23. Testing Strategy

### 23.1 Test Levels

| Level | Framework | Coverage Target | Environment |
|-------|-----------|----------------|-------------|
| **Unit** | pytest | > 90% line | CI |
| **Integration** | pytest + testcontainers | > 80% path | CI (staging DB) |
| **E2E** | pytest + testcontainers | All major paths | Staging |
| **Performance** | k6 + custom | Meet P50/P95 targets | Staging |
| **Chaos** | Chaos Mesh | Graceful degradation | Staging |
| **Security** | Semgrep + custom | Zero critical/high | CI + staging |

### 23.2 Test Scenarios

Connector Tests: connect_success, connect_failure, connect_timeout, connect_permission_denied, fetch_databases_empty, fetch_tables_1000, fetch_columns_composite, fetch_pg_catalog_excluded.

Pipeline Tests: full_sync_200_tables, incremental_sync_10_tables, sync_no_changes, sync_cancel_midway, sync_parallel_workers, large_schema_10000_tables, schema_change_detection, column_rename_detection.

Annotation Tests: annotation_cryptic_name, annotation_business_entity, annotation_semantic_type, annotation_confidence_low, annotation_llm_failure, annotation_batch_100.

Profiling Tests: profiling_fast_mode, profiling_null_ratio, profiling_empty_table, profiling_large_table, profiling_timeout.

Isolation Tests: tenant_isolation_sync, tenant_isolation_query, tenant_rate_limit_enforced, tenant_delete_gdpr.

### 23.3 Test Data Requirements

| Dataset | Type | Tables | Source |
|---------|------|--------|--------|
| Northwind | PostgreSQL | 13 | Open source |
| StackOverflow | PostgreSQL | 8 | Open source |
| IMDB | PostgreSQL | 7 | Open source |
| AdventureWorks | SQL Server | 70+ | Microsoft sample |
| TPC-H | PostgreSQL | 8 | Industry standard |
| TPC-DS | PostgreSQL | 24 | Industry standard |
| Obscure naming | Custom | 50 | Synthetic |
| Large schema | Custom | 10,000 | Synthetic |

### 23.4 Acceptance Criteria

- [ ] Unit tests pass in < 5 minutes
- [ ] Integration tests pass in < 15 minutes
- [ ] E2E tests pass in < 30 minutes
- [ ] All connector implementations tested against real database instances
- [ ] Performance tests meet P50/P95 latency targets
- [ ] Security tests verify tenant isolation and injection prevention

---

## 24. Monitoring Metrics

### 24.1 Key Metrics

| Metric | Type | Alert Threshold |
|--------|------|----------------|
| si_sync_duration_seconds | Histogram | P95 > 300s |
| si_sync_tables_per_second | Gauge | < 1 table/s sustained |
| si_sync_errors_total | Counter | > 5 per hour |
| si_annotation_latency_seconds | Histogram | P95 > 10s |
| si_annotation_confidence | Histogram | Median < 0.7 |
| si_profiling_duration_seconds | Histogram | P95 > 30s |
| si_profiling_errors_total | Counter | > 10 per hour |
| si_embedding_latency_seconds | Histogram | P95 > 2s per 100 items |
| si_change_detection_latency | Histogram | P95 > 30s |
| si_schema_versions_created | Counter | Rate tracking |
| si_tenant_active_extractions | Gauge | Per-tenant tracking |
| si_pool_workers_busy | Gauge | > 80% for > 5 min |
| si_connector_errors_by_db_type | Counter | Alert on new type |
| si_storage_usage_bytes | Gauge | > 80% capacity |

### 24.2 Dashboards

**Schema Intelligence Health**: Sync duration (P50/P95/P99), errors by stage, active extractions, worker pool utilization, LLM annotation latency, embedding queue depth.

**Schema Coverage**: Total tables discovered, % annotated, % with semantic type, % relationships discovered, business entities detected, average confidence.

**Schema Change Activity**: Versions created per day, changes by type, top 10 most volatile tables, sync schedule adherence.

### 24.3 Alerting Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| Sync failure rate high | > 5 errors/hour | Warning |
| Sync stuck | Job running > 2x expected duration | Warning |
| LLM annotation down | Error rate > 10% in 5 min | Critical |
| Embedding service down | Queue growing > 100 | Critical |
| Storage near capacity | Usage > 80% | Warning |
| Tenant isolation breach | Cross-tenant read detected | Critical |
| Large schema sync timeout | Sync > 4 hours for one DB | Warning |

### 24.4 Acceptance Criteria

- [ ] All metrics exported in Prometheus format
- [ ] Dashboards created in Grafana
- [ ] Alert rules configured with correct severity and notification channels
- [ ] Metrics retained for 30 days + 1 year long-term
- [ ] Every alert has a documented runbook

---

## 25. Future Improvements

### 25.1 Post-MVP Enhancements

| Improvement | Value | Complexity | Timeline |
|-------------|-------|------------|----------|
| Document ingestion (data dictionaries, ERDs) | High | High | Month 6 |
| Historical query mining for join patterns | Medium | Medium | Month 4 |
| Automatic data dictionary PDF generation | Medium | Medium | Month 5 |
| Data lineage visualization | High | High | Month 8 |
| Schema comparison UI | Low | Low | Month 3 |
| Custom connector SDK | High | High | Month 9 |
| CDC-based streaming (Debezium) | High | High | Month 10 |
| ML-based relationship scoring | Medium | Medium | Month 6 |
| Self-tuning sync frequency | Low | Low | Month 4 |
| Schema impact analysis | High | High | Month 12 |
| Multi-source schema merge | High | High | Month 8 |
| Schema quality scoring | Low | Low | Month 5 |

### 25.2 Research Areas

| Area | Question | Approach |
|------|----------|---------|
| LLM-free annotation | Can we match LLM quality without LLM? | Pattern library from known schemas |
| Cross-tenant learning | Learn from anonymized patterns | Federated learning |
| Schema embedding compression | Reduce 1024-d without loss | Quantization, Matryoshka |
| Automatic FK discovery | > 95% precision without explicit FKs? | ML classifier on column pairs |

---

## Appendix A: Cross-References

| Schema Intelligence | Related Document | Relationship |
|--------------------|-----------------|--------------|
| Metadata extraction | KnowledgeEngine-Specification.md \u00a72 | Schema store is primary knowledge source |
| Annotator + Embedder | KnowledgeEngine-Specification.md \u00a73 | Schema intelligence feeds schema enrichment |
| Business glossary | KnowledgeEngine-Specification.md \u00a76 | Glossary terms \u2192 knowledge graph nodes |
| Relationship graph | KnowledgeEngine-Specification.md \u00a75 | Relationships stored as graph edges |
| KE API integration | API-Specification.md \u00a77 | Schema intelligence triggered via KE API |
| Schema sync API | API-Specification.md \u00a76.5 | Public sync trigger endpoint |
| Database tables | Database-Specification.md \u00a75 | Table definitions for schema store |
| Performance budgets | Performance-Specification.md \u00a71 | Latency budgets for sync operations |
| Embedding costs | Performance-Specification.md \u00a76 | BGE-M3 embedding costs |
| Storage costs | Performance-Specification.md \u00a77 | Schema store storage costs |
| AI agent spec | AI-Agent-Specification.md \u00a72 | Retriever agent consumes schema embeddings |
| Multi-tenant isolation | Security-Specification.md \u00a710 | Tenant isolation design |
| Schema security | Security-Specification.md \u00a75 | RBAC for schema access |
| Infrastructure deployment | Infrastructure-Specification.md \u00a717 | GPU pod for embedder deployment |

## Appendix B: Risks and Assumptions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM annotation quality degrades for industry jargon | Medium | Medium | Rule-based fallback, fine-tuning |
| Database connector breaks due to upstream changes | Low | High | Abstract interface, integration tests |
| Large schema extraction overwhelms source DB | Medium | High | Rate limiting, read replica preference |
| Sample data contains PII despite best efforts | Low | Critical | Data classification, masking, retention limits |
| Cross-tenant data leak in shared Qdrant | Low | Critical | Per-tenant collections, isolation tests |
| LLM service dependency outage | Medium | Medium | Rule-based fallback, *UNKNOWN* convention |

### Assumptions

| Assumption | Impact if Wrong | Validation |
|------------|----------------|------------|
| Source databases expose information_schema | Connector modules fail | Validated during implementation |
| Column names contain meaningful signals | Detection accuracy drops | Research spike EP-017 |
| LLM annotation achieves > 70% helpful rating | User trust degrades | Research spike EP-017 |
| Customers permit sample data extraction | Profiling accuracy limited | Configurable opt-in |
| Schemas change at most weekly | Incremental sync handles load | Production monitoring |
| 5 DB dialects cover > 80% of market | Market segments inaccessible | Phase 1 market analysis |

## Appendix C: Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-10 | Principal Data Platform Architect | Initial specification \u2014 25 sections covering all Schema Intelligence subsystems |

---
*End of Schema-Specification.md*
