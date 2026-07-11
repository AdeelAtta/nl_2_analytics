# ADR-019: Ontology Service

| Metadata | Value |
|----------|-------|
| **ADR ID** | ADR-019 |
| **Date** | 2026-07-11 |
| **Status** | Accepted |
| **Supersedes** | — |

---

## Context

Raw database schemas provide tables, columns, and foreign keys but lack semantic meaning. To generate accurate NL2SQL queries, the platform needs a knowledge graph that captures domain-specific relationships, synonyms, business concepts, and query patterns. This ontology enriches schema context with human-curated meaning, enabling the query generator to understand that "customer_id" and "client_number" refer to the same entity, or that certain columns are frequently joined.

## Decision

Implement an ontology service backed by a PostgreSQL graph store (adjacency list model with recursive CTE traversal) that manages typed nodes and typed edges:

### Node Types

| Node Type | Description |
|-----------|-------------|
| `table` | Database table reference |
| `column` | Database column reference |
| `domain` | Business domain grouping (e.g., "Sales", "Inventory") |
| `concept` | Abstract business concept (e.g., "Customer Lifetime Value") |
| `glossary_term` | Business glossary entry with definition |
| `query_pattern` | Reusable query pattern (e.g., "Monthly active users") |

### Edge Types

| Edge Type | Description |
|-----------|-------------|
| `belongs_to` | Child-to-parent containment (column → table, table → domain) |
| `references` | Foreign key or logical reference between columns |
| `maps_to` | Synonym/alias mapping (e.g., "customer_id" → "client_number") |
| `frequently_joined` | Tables commonly joined together (with join count metadata) |
| `semantic_parent` | Generalized hierarchy (concept → broader concept) |

Key design decisions:

- **PostgreSQL adjacency list**: Nodes and edges stored in separate tables (`graph_nodes`, `graph_edges`) with JSONB properties. Graph traversal uses recursive CTEs for path finding.
- **Multi-tenant**: All nodes and edges are scoped by `tenant_id` for strict isolation.
- **Import/export**: Supports JSON and YAML formats with merge (additive) or replace (destructive) modes. Import preserves external IDs for idempotent re-imports.
- **REST API**: Full CRUD for nodes and edges plus dedicated import/export/traverse endpoints.
- **Flexible properties**: Nodes and edges carry a `properties` JSONB field for arbitrary metadata.

## Rationale

- **PostgreSQL over graph DB**: Avoids operational complexity of a dedicated graph database. The graph is small (< 100K nodes) and does not require horizontal scaling. Recursive CTEs provide adequate performance for path traversal.
- **Adjacency list over other models**: Simple, well-understood, supports efficient CRUD. No need for materialized path or nested sets for this workload.
- **JSONB properties**: Schema flexibility without migration overhead. Properties vary per node type (e.g., a `table` node has `schema_name`, a `glossary_term` has `definition`).
- **Merge vs replace**: Merge enables incremental updates from trusted sources; replace supports full reimport. Both are useful in different scenarios.
- **Typed nodes and edges**: Enforces structure while allowing extensibility via JSONB properties.

## Consequences

### Positive
- Semantic enrichment improves NL2SQL accuracy for domain-specific queries
- Import/export enables ontology transfer between environments (dev → staging → prod)
- Recursive CTE traversal works without additional infrastructure
- REST API makes the ontology accessible to external tools and frontends

### Negative
- Recursive CTE performance degrades beyond ~10 depth levels (acceptable for expected tree depths)
- No graph-native query language (Cypher, Gremlin) — complex graph algorithms are impractical
- JSONB properties lack referential integrity and schema validation
- Ontology maintenance requires human curation — it does not self-populate

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| Dedicated graph database (Neo4j, ArangoDB) | Additional operational cost and complexity; not justified for expected graph size (< 100K nodes) |
| In-memory graph | Does not survive restarts; no import/export; limited to single instance |
| No ontology (schema-only) | Lacks semantic enrichment needed for domain-specific query accuracy |

## References

- `ke/services/ontology.py` — `OntologyService` (import/export)
- `ke/models/graph.py` — `GraphNode`, `GraphEdge`, `GraphPath`, `NodeType`, `EdgeType`
- `ke/stores/graph/repository.py` — `GraphNodeRepository`, `GraphEdgeRepository` with recursive CTE traversal
- `ke/api/routes/graph.py` — REST API endpoints
