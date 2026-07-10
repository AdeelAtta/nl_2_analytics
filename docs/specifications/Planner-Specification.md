# Planner Specification

**Enterprise Data Intelligence Platform — Query Planning Subsystem**

| Metadata | Value |
|----------|-------|
| **Author** | Principal AI Planning Architect |
| **Date** | 2026-07-10 |
| **Status** | Approved |
| **Version** | 1.0 |
| **Architecture Reference** | System-Architecture.md \u00a73.3, Component-Design.md \u00a75 |
| **Cross-References** | AI-Agent-Specification.md \u00a74, KnowledgeEngine-Specification.md \u00a75-6, API-Specification.md \u00a78.3, Performance-Specification.md \u00a71, \u00a75, Database-Specification.md \u00a56, Schema-Specification.md \u00a76 |

---

## 1. Planner Responsibilities

### 1.1 Mission

Transform a natural language query and its retrieved context into an executable query plan \u2014 a structured, validated sequence of SQL operations that can be generated, executed, and verified. The Planner bridges the gap between what the user asked and how the database must answer it.

### 1.2 Primary Responsibilities

| Responsibility | Description | Failure Mode |
|---------------|-------------|-------------|
| **Intent classification** | Determine query type: simple SELECT, aggregation, multi-join, cross-DB, analytical, DDL | Misclassification leads to incorrect plan structure |
| **Query decomposition** | Break complex questions into sub-questions that can be composed | Over-decomposition creates unnecessary joins |
| **Multi-step reasoning** | Plan intermediate steps: which tables to join first, which filters to apply, which aggregations to compute | Wrong order produces wrong results |
| **Join planning** | Discover join paths, select join types, determine join order | Missing or incorrect joins cause wrong results |
| **Aggregation planning** | Identify grouping columns, aggregate functions, HAVING filters | Wrong grouping produces wrong aggregations |
| **Window function planning** | Detect window operations, plan PARTITION BY and ORDER BY | Incorrect window specification |
| **Subquery planning** | Identify subquery candidates, plan correlation vs uncorrelated | Inefficient or incorrect subqueries |
| **Cost estimation** | Estimate row counts, join selectivity, execution cost | Poor estimates lead to bad plan choices |
| **Plan validation** | Verify plan correctness against schema and constraints | Invalid plans waste generation + execution |
| **Reflection loop** | Self-correct based on validation errors | Uncaught errors propagate to generation |
| **Memory management** | Track plan state across reflection cycles | Lost context forces full replan |

### 1.3 Non-Responsibilities

| Not Responsible For | Handled By |
|--------------------|------------|
| Retrieving schema context | Context Retriever (AI-Agent-Spec.md \u00a73) |
| Generating SQL text | SQL Generator (AI-Agent-Spec.md \u00a75) |
| Executing queries | Query Executor (EP-011) |
| Validating SQL syntax | Validator Agent (AI-Agent-Spec.md \u00a76) |
| Repairing failed SQL | Repair Agent (AI-Agent-Spec.md \u00a78) |
| Policy enforcement | Policy Enforcement Stack (AI-Agent-Spec.md \u00a77) |

### 1.4 Architecture Rationale

**Why a separate Planner instead of end-to-end generation?**

End-to-end SQL generation (query \u2192 SQL) treats planning as an implicit step inside the LLM. This fails for complex queries because:

1. **No explicit intermediate representation**: The LLM must hold the entire plan in its context window. For 10-table joins with nested subqueries, this exceeds effective context.
2. **No validation before generation**: Errors are discovered after SQL generation, wasting inference cost on invalid plans.
3. **No structured cost estimation**: The LLM cannot accurately estimate row counts or join selectivity in a single pass.
4. **No decomposition for complex questions**: Questions requiring multiple sub-answers (e.g., "which products had above-average sales in each region last quarter?") need explicit sub-goal planning.

The Planner produces a **QueryPlan** object \u2014 a structured intermediate representation that the Generator converts to SQL. This separation enables:

- Validation at the plan level (before SQL generation cost)
- Cost estimation at each step (informs join order, subquery strategy)
- Decomposition into sub-plans (parallel or sequential execution)
- Memory across reflection cycles (re-plan specific steps, not the whole query)

---

## 2. Planner Architecture

### 2.1 Component Diagram

```
+------------------------------------------------------------------+
|                        QUERY PLANNER                              |
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  |   Intent         |  |   Decomposer     |  |   Join Planner   | |
|  |   Classifier     |  |                  |  |                  | |
|  +--------+---------+  +-------+----------+  +--------+---------+ |
|           |                     |                      |          |
|           v                     v                      v          |
|  +------------------+  +------------------+  +------------------+ |
|  |   Aggregation    |  |   Window         |  |   Subquery       | |
|  |   Planner        |  |   Planner        |  |   Planner        | |
|  +--------+---------+  +--------+---------+  +--------+---------+ |
|           |                     |                      |          |
|           +---------------------+----------------------+          |
|                                 |                                 |
|                                 v                                 |
|  +------------------+  +------------------+  +------------------+ |
|  |   Cost Estimator |  |   Plan Validator |  |   Plan Builder   | |
|  |                  |  |                  |  |                  | |
|  +------------------+  +------------------+  +--------+---------+ |
|                                                        |          |
|                                                        v          |
|  +------------------+                                +-------+   |
|  |   Reflection     |<--- validation errors ---------|       |   |
|  |   Controller     |----> re-plan instructions -----|       |   |
|  +------------------+                                +-------+   |
|                                                        |          |
|  +------------------+                                 |          |
|  |   Plan Memory    |<--- plan state storage ---------|          |
|  +------------------+                                 |          |
|                                                        v          |
|                                                 +--------------+  |
|                                                 | QueryPlan    |  |
|                                                 | (to Generator)| |
|                                                 +--------------+  |
+------------------------------------------------------------------+
        |                    |                       |
        v                    v                       v
   Knowledge Engine    Schema Store            Metric Store
   (resolve terms)     (tables, cols, FKs)     (business metrics)
```

### 2.2 Data Flow

```
User Query + Context (from Retriever)
    |
    v
[1. Intent Classifier]
    |--- Determines: query type, complexity, expected result shape
    |--- Outputs: QueryIntent { type, tables, confidence }
    v
[2. Decomposer]
    |--- Breaks compound questions into sub-questions
    |--- Identifies dependencies between sub-questions
    |--- Outputs: list of SubQuery { goal, dependencies }
    v
[3. Join Planner]
    |--- Discovers join paths via Knowledge Graph
    |--- Selects join types (INNER, LEFT, RIGHT, FULL, CROSS)
    |--- Determines join order (cost-based)
    |--- Outputs: JoinPlan { edges, order, types }
    v
[4. Aggregation Planner]
    |--- Identifies GROUP BY columns
    |--- Selects aggregate functions (SUM, AVG, COUNT, MIN, MAX)
    |--- Plans HAVING filters
    |--- Outputs: AggregationPlan { group_by, aggregates, having }
    v
[5. Window Function Planner]
    |--- Detects window operations (RANK, ROW_NUMBER, LAG, LEAD)
    |--- Plans PARTITION BY and ORDER BY clauses
    |--- Outputs: WindowPlan { functions, partitions, ordering }
    v
[6. Subquery Planner]
    |--- Identifies subquery candidates (WHERE IN, EXISTS, derived tables)
    |--- Plans correlated vs uncorrelated execution
    |--- Outputs: SubqueryPlan { type, correlation, nesting }
    v
[7. Cost Estimator]
    |--- Estimates row counts per plan step
    |--- Estimates join selectivity
    |--- Estimates execution cost (relative)
    |--- Outputs: CostEstimate { rows, cost, selectivity }
    v
[8. Plan Validator]
    |--- Validates join paths exist and are accessible
    |--- Validates columns exist in selected tables
    |--- Validates aggregate/window functions match column types
    |--- Validates subquery structure
    |--- Outputs: ValidationResult { valid, errors[] }
    v
[9. Plan Builder]
    |--- Assembles all sub-plans into unified QueryPlan
    |--- Orders plan steps (topological sort)
    |--- Outputs: QueryPlan { steps, dependencies, metadata }
    v
[10. Reflection Controller]
    |--- If validation fails: identify failing step, re-plan
    |--- If validation passes: emit QueryPlan to Generator
    |--- Max 2 reflection cycles
```

### 2.4 Multi-Step Reasoning

The Planner employs a chain-of-thought reasoning process that decomposes the planning task into a sequence of explicit intermediate decisions. Each decision builds on the previous one, creating a transparent audit trail.

#### Reasoning Chain

```
Step 1: What is the user asking for?
  -> Intent classification
  -> "This is an aggregation query over orders and customers"

Step 2: What information do I need?
  -> Schema resolution
  -> "I need: orders table, customers table, join on customer_id"

Step 3: How do the pieces connect?
  -> Relationship discovery
  -> "orders.customer_id -> customers.id (FK, confidence 1.0)"

Step 4: What operations are needed?
  -> Operation planning
  -> "FILTER by date range, JOIN customer name, GROUP BY region, SUM sales"

Step 5: In what order should operations execute?
  -> Step ordering
  -> "SCAN orders (filtered) -> JOIN customers -> AGGREGATE -> SORT -> PROJECT"

Step 6: How much will this cost?
  -> Cost estimation
  -> "Estimated 5,000 rows, relative cost 120"

Step 7: Is this plan correct?
  -> Validation
  -> "All tables and columns valid, join paths exist, types compatible"

Step 8: (If invalid) What went wrong and how to fix it?
  -> Reflection
  -> "Missing column 'region' in orders table; suggest 'order_region' instead"
```

#### Reasoning Principles

| Principle | Description | Enforced By |
|-----------|-------------|-------------|
| **Explicit state** | Each reasoning step produces a visible intermediate result | PlanStep objects |
| **Verifiable decisions** | Every decision references evidence (schema, relationship, cost) | Decision trace in plan memory |
| **Minimal LLM dependency** | LLM used only for ambiguity resolution, not routine reasoning | Tool selection policy (\u00a711.2) |
| **Bounded depth** | Reasoning chain limited to the minimum steps needed | Plan complexity classification |
| **Reversible decisions** | Every decision can be revisited during reflection | Reflection loop (\u00a714) |
| **Parallel reasoning** | Independent sub-queries reasoned about in parallel | Decomposition model (\u00a74) |

#### Reasoning by Query Complexity

| Complexity | Reasoning Depth | LLM Calls | Typical Steps |
|------------|----------------|-----------|---------------|
| Simple | 3 steps (classify, locate, validate) | 0 | 5-10 PlanSteps |
| Medium | 5 steps (classify, decompose, locate, plan, validate) | 0-1 | 10-20 PlanSteps |
| Complex | 7 steps (classify, decompose, locate, plan joins, plan aggs, cost, validate) | 1-2 | 20-40 PlanSteps |
| Very Complex | 8-10 steps (full chain with reflection) | 2-3 | 40-80 PlanSteps |

### 2.5 QueryPlan Object Structure

```
QueryPlan {
    id: UUID
    query_intent: QueryIntent
    sub_queries: [SubQuery]
    join_plan: JoinPlan
    aggregation_plan: AggregationPlan | null
    window_plan: WindowPlan | null
    subquery_plan: SubqueryPlan | null
    cost_estimate: CostEstimate
    validation: ValidationResult
    plan_steps: [PlanStep]          // Ordered execution steps
    metadata: PlanMetadata {
        complexity: "simple" | "medium" | "complex"
        table_count: int
        join_count: int
        subquery_count: int
        estimated_rows: int
        estimated_cost: float
        reflection_count: int
    }
}
```

---

## 3. Intent Classification

### 3.1 Query Types

| Type | Description | Examples | Plan Complexity |
|------|-------------|----------|-----------------|
| **SIMPLE_SELECT** | Single table, no joins, no aggregation | "Show all customers" | Low |
| **FILTERED_SELECT** | Single table with WHERE conditions | "Find orders from last month" | Low |
| **JOIN** | Multi-table query with joins | "Show orders with customer names" | Medium |
| **AGGREGATION** | GROUP BY with aggregate functions | "Total sales by region" | Medium |
| **COMPOUND** | Multiple sub-queries composed | "Products with above-average sales" | High |
| **WINDOW** | Window functions (ranking, running totals) | "Rank employees by salary" | High |
| **SUBQUERY** | Nested queries (IN, EXISTS, derived) | "Customers who placed > 5 orders" | High |
| **CROSS_DB** | Cross-database joins | "Compare sales CRM vs ERP" | Very High |
| **ANALYTICAL** | Complex OLAP (ROLLUP, CUBE, PIVOT) | "Monthly sales by product category" | Very High |
| **DDL** | Schema changes (not supported in MVP) | "Create a view of active customers" | N/A (rejected) |

### 3.2 Classification Method

The Intent Classifier uses a lightweight classifier (not the full LLM) to determine query type within 50ms:

```
Level 1: Rule-based pattern matching on query text
  - Contains "join" or "together with"            -> JOIN
  - Contains "average", "total", "count", "sum"    -> AGGREGATION
  - Contains "rank", "row number", "top N"         -> WINDOW
  - Contains "compared to", "versus", "vs"         -> COMPOUND
  - Contains "create", "alter", "drop", "insert"   -> DDL (reject)

Level 2: Entity-based classification on retrieved context
  - query references tables from multiple databases -> CROSS_DB
  - query references > 4 tables                    -> COMPLEX join
  - query references 1-2 tables + aggregate keyword -> AGGREGATION

Level 3: LLM fallback for ambiguous queries
  - If Level 1+2 confidence < 0.8
  - Use lightweight LLM call (SQLCoder-7B) with yes/no prompt
```

### 3.3 Confidence Scoring

| Factor | Weight | Description |
|--------|--------|-------------|
| Pattern match strength | 0.4 | How many patterns matched the type |
| Entity match | 0.3 | Do the entities (tables, columns) support the type |
| Schema compatibility | 0.2 | Does the schema support the implied operations |
| LLM signal (if used) | 0.1 | LLM classification confidence |

**Thresholds**: Accept at \u2265 0.8. Flag for human review at < 0.8. Return error at < 0.5.

---

## 4. Query Decomposition

### 4.1 When to Decompose

| Condition | Example | Decomposition Strategy |
|-----------|---------|----------------------|
| Multiple independent questions | "Show customers from NY and total sales by region" | Split into sub-queries, execute in parallel |
| Comparative question | "Compare Q1 sales to Q2 sales" | Two sub-queries with shared context |
| Conditional sub-question | "Find products whose sales exceeded the average" | Inner sub-query computes average, outer compares |
| Multi-step analytical | "Which region had the highest growth rate?" | Step 1: sales by region per period. Step 2: compute growth. Step 3: find max. |
| Cross-database question | "Show orders from MySQL and customer details from PostgreSQL" | Per-database sub-queries, merge results |

### 4.2 Decomposition Algorithm

```
Input: User query, QueryIntent, Retrieved context
Output: List of SubQuery objects

Algorithm:
1. Parse query for coordinating conjunctions (and, but, while, versus)
2. For each conjunct, extract the subject and predicate
3. Check if extracted sub-queries share tables
   - Shared tables -> sequential execution (join results)
   - Independent tables -> parallel execution possible
4. For comparative questions, identify the comparison dimension
   - Create sub-query for each comparison group
5. For conditional questions, identify the condition
   - Inner sub-query supplies the condition value
   - Outer sub-query uses it as filter
6. Assign dependency order based on data flow
7. Validate each sub-query against schema
```

### 4.3 SubQuery Object

```
SubQuery {
    id: UUID
    goal: string                    // Natural language description
    parent_query_id: UUID           // References parent plan
    query_intent: QueryIntent        // Sub-type
    dependencies: [UUID]            // Sub-queries that must complete first
    tables: [TableRef]
    join_plan: JoinPlan | null
    aggregation_plan: AggregationPlan | null
    window_plan: WindowPlan | null
    execution_mode: "sequential" | "parallel" | "conditional"
    status: "pending" | "planned" | "validated" | "failed"
}
```

### 4.4 Decomposition Examples

| Original Query | Sub-Queries | Execution |
|----------------|-------------|-----------|
| "Show customers from NY and total sales by region" | Q1: customers in NY; Q2: sales by region | Parallel |
| "Compare Q1 2024 vs Q1 2025 revenue" | Q1: revenue Q1 2024; Q2: revenue Q1 2025 | Parallel, merged |
| "Products with above-average order value" | Q1: average order value; Q2: products > that value | Sequential (Q1 \u2192 Q2) |
| "Which region grew fastest last year?" | Q1: sales by region per quarter; Q2: growth rate; Q3: max growth | Sequential (Q1 \u2192 Q2 \u2192 Q3) |

---

## 5. Join Planning

### 5.1 Join Path Discovery

```
Input: Set of tables referenced in query, Knowledge Graph
Output: Ordered list of join edges

Algorithm:
1. Collect all referenced tables from query + retrieved context
2. Query Knowledge Graph for existing relationship edges between tables
3. For table pairs without known relationships:
   a. Look up shared column names (same name, compatible types)
   b. Look up potential FK patterns (table_id, table_fk)
   c. Score candidate relationships by confidence (Schema-Spec.md \u00a76)
4. Build a graph of table-relationship pairs
5. Find minimum spanning tree connecting all referenced tables
6. For remaining disconnected tables, flag as potential cross-join
7. Order join edges by:
   a. Highest confidence first
   b. Smallest table first (row count heuristic)
   c. Filtering joins before expanding joins
```

### 5.2 Join Type Selection

| Condition | Preferred Join Type | Rationale |
|-----------|-------------------|-----------|
| FK relationship exists, both sides required | INNER JOIN | Most efficient, guaranteed match |
| FK relationship exists, right side optional | LEFT JOIN | Preserve left rows when right may be missing |
| FK relationship exists, left side optional | RIGHT JOIN | Preserve right rows (rare in practice) |
| All rows from both sides needed | FULL OUTER JOIN | Complete union (analytical queries) |
| No relationship, intentional Cartesian product | CROSS JOIN | Rare, usually indicates missing join condition |
| Self-referencing table (e.g., org chart) | Self-JOIN | Requires table alias |

### 5.3 Join Order Optimization

```
Heuristic-based join ordering (cost-based optimization deferred to v2):

1. Start with the table having the most restrictive filter (lowest estimated rows)
2. Join the next table with the strongest relationship (highest confidence FK)
3. Apply filters as early as possible in the join sequence
4. Push aggregations before joins where semantically valid
5. Limit number of joins to:
   - Simple: \u2264 2 joins
   - Medium: 3-5 joins
   - Complex: 6-10 joins
   - Very complex: > 10 joins (flag for review)

Join order estimation cost calculated as:
  cost(order) = sum(row_estimate(intermediate_result)) for each join step
  Select order with minimum total intermediate row count
```

### 5.4 Cross-Database Join Handling

```
Cross-database joins require special planning:

1. Identify which tables belong to which database
2. Determine if database supports cross-DB queries (e.g., PG foreign data wrappers)
3. If cross-DB query supported: plan federated query
4. If not supported: plan result-set merge
   a. Execute sub-query on each database independently
   b. Fetch all results to planner
   c. Perform in-memory merge on the join key
   d. Flag to user: "Results merged from multiple databases"

Limitations:
  - In-memory merge limited to 10K rows per side
  - Cross-DB joins flagged as "approximate" in result metadata
  - Cross-DB join latency: P95 < 30s (network transfer dominant)
```

---

## 6. Aggregation Planning

### 6.1 Aggregate Function Detection

| User Language | Aggregate Function | Notes |
|---------------|-------------------|-------|
| "total", "sum", "combined" | SUM() | Numeric columns only |
| "average", "mean", "avg", "typical" | AVG() | Numeric columns only |
| "count", "how many", "number of" | COUNT() | Any column; COUNT(*) for rows |
| "minimum", "min", "smallest", "lowest" | MIN() | Ordered columns |
| "maximum", "max", "largest", "highest" | MAX() | Ordered columns |
| "distinct", "unique" | COUNT(DISTINCT) | With COUNT modifier |
| "variance", "variation" | VAR() | Post-MVP |
| "standard deviation", "stddev" | STDDEV() | Post-MVP |

### 6.2 GROUP BY Column Selection

```
Algorithm for identifying grouping columns:

1. Extract non-aggregated columns referenced in SELECT context
2. For each non-aggregated column:
   a. Check if it's the primary dimension of the question ("by region", "per month")
   b. If yes, add to GROUP BY
3. Validate grouping column exists in selected tables
4. Check functional dependency:
   - If grouping by a PK, other columns from same table are valid
   - If grouping by non-PK, all non-aggregated columns must be in GROUP BY
5. Determine grouping level:
   - Column level (group by region)
   - Temporal rollup (group by month, quarter, year)
   - Multi-level (group by region, product)
```

### 6.3 HAVING Filter Planning

```
HAVING filters are planned when:

1. Query contains "with" or "having" followed by aggregate condition
   Example: "regions with total sales > 1M"
   Plan: GROUP BY region, HAVING SUM(sales) > 1000000

2. Query compares aggregate result to threshold
   Example: "products ordered more than 100 times"
   Plan: GROUP BY product, HAVING COUNT(*) > 100

3. Query contains aggregate comparison
   Example: "average order value > $50"
   Plan: AVG(order_total) as avg_value, HAVING avg_value > 50
```

### 6.4 Complex Aggregation Patterns

| Pattern | SQL Structure | Planning Notes |
|---------|--------------|----------------|
| GROUP BY + HAVING | GROUP BY cols HAVING agg_condition | Plan HAVING after GROUP BY |
| GROUP BY + ORDER BY | GROUP BY cols ORDER BY agg DESC | Plan sort on aggregate |
| ROLLUP | GROUP BY ROLLUP(cols) | Post-MVP, hierarchical totals |
| CUBE | GROUP BY CUBE(cols) | Post-MVP, all combinations |
| GROUPING SETS | GROUP BY GROUPING SETS(...) | Post-MVP, custom groupings |
| FILTER (WHERE agg) | agg FILTER (WHERE condition) | Conditional aggregation |
| Multiple aggregates | SELECT SUM(x), AVG(y), COUNT(z) | All planned as sibling steps |

---

## 7. Window Function Planning

### 7.1 Window Function Detection

| User Language | Window Function | SQL Equivalent |
|---------------|----------------|----------------|
| "rank by", "ranking" | RANK() | RANK() OVER (ORDER BY col) |
| "row number", "number rows" | ROW_NUMBER() | ROW_NUMBER() OVER (ORDER BY col) |
| "dense rank" | DENSE_RANK() | DENSE_RANK() OVER (ORDER BY col) |
| "previous", "lag", "earlier" | LAG() | LAG(col, 1) OVER (ORDER BY col) |
| "next", "lead", "later" | LEAD() | LEAD(col, 1) OVER (ORDER BY col) |
| "first", "earliest" | FIRST_VALUE() | FIRST_VALUE(col) OVER (...) |
| "last", "most recent" | LAST_VALUE() | LAST_VALUE(col) OVER (...) |
| "running total", "cumulative" | SUM() OVER | SUM(col) OVER (ORDER BY col) |
| "moving average", "rolling" | AVG() OVER | AVG(col) OVER (ORDER BY col ROWS N PRECEDING) |
| "percentile", "ntile" | NTILE() | NTILE(N) OVER (ORDER BY col) |

### 7.2 PARTITION BY Planning

```
PARTITION BY columns are inferred from:

1. Explicit grouping in query: "rank products by sales within each category"
   -> PARTITION BY category ORDER BY sales DESC

2. Hierarchical context: "top employee per department"
   -> PARTITION BY department ORDER BY ... 

3. Temporal partitions: "running total by month"
   -> PARTITION BY EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date)

Algorithm:
1. Extract the grouping dimension from query context
2. If no explicit partition, use the natural grouping (no PARTITION BY)
3. Validate partition column exists in the table
4. For temporal partitions, plan date extraction functions
```

### 7.3 Window Frame Specification

| Frame Type | When Used | SQL |
|------------|-----------|-----|
| Default (entire partition) | RANK, ROW_NUMBER, aggregate over all rows | ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING |
| Cumulative | Running totals, growth | ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW |
| Moving window | Moving averages, rolling sums | ROWS BETWEEN N PRECEDING AND CURRENT ROW |
| Centered window | Smoothing | ROWS BETWEEN N PRECEDING AND N FOLLOWING |

---

## 8. Subquery Planning

### 8.1 Subquery Types

| Type | SQL Pattern | Use Case | Planning Strategy |
|------|-------------|----------|-------------------|
| Scalar subquery | (SELECT AVG(x) FROM t) | Compare to aggregate | Execute first, cache result |
| Row subquery | (SELECT x, y FROM t WHERE ...) | Multi-column filter | Join-like plan |
| Table subquery (derived) | FROM (SELECT ...) AS sub | Intermediate result | Materialize or inline |
| EXISTS subquery | WHERE EXISTS (SELECT ...) | Existence check | Correlated or not |
| IN subquery | WHERE x IN (SELECT ...) | Membership | Semi-join or materialize |
| NOT IN subquery | WHERE x NOT IN (SELECT ...) | Negative membership | Anti-semi-join, handle NULLs |
| ANY/ALL subquery | WHERE x > ANY (SELECT ...) | Comparative | Rewrite as MIN/MAX |

### 8.2 Correlation Detection

```
A subquery is correlated if it references columns from the outer query.

Detection:
1. Parse subquery WHERE clause
2. Check for column references that resolve to outer query tables
3. If correlated:
   - Plan subquery execution for each outer row
   - Provide index recommendation if performance concern
   - Flag as potential performance issue
4. If uncorrelated:
   - Execute subquery once, cache result
   - Prefer semi-join rewrite for IN/EXISTS

Correlated subquery optimization candidates:
  - IN (SELECT ...) -> EXISTS rewrite when outer is large
  - NOT IN (SELECT ...) -> NOT EXISTS rewrite (handles NULLs correctly)
  - Scalar aggregate subquery -> LEFT JOIN rewrite
```

### 8.3 Subquery Nesting Depth

| Depth | Plan Strategy | Risk |
|-------|---------------|------|
| 1 level | Direct execution | Low |
| 2 levels | Sequential execution, materialize intermediate | Medium |
| 3+ levels | Break into CTEs, sequential execution | High (complexity warning) |
| 5+ levels | Reject, suggest user simplifies query | Very High |

---

## 9. Execution Plan Generation

### 9.1 PlanStep Structure

```
PlanStep {
    id: UUID
    step_number: int                   // Execution order
    operation: PlanOperation           // See below
    dependencies: [UUID]               // Steps that must complete first
    tables: [TableRef]
    columns: [ColumnRef]
    filters: [FilterExpression]
    joins: [JoinEdge]
    grouping: GroupingSpec | null
    aggregation: AggregationSpec | null
    window: WindowSpec | null
    subquery: SubquerySpec | null
    ordering: [OrderSpec]
    limit: int | null
    estimated_cost: float
    estimated_rows: int
    metadata: StepMetadata
}
```

### 9.2 PlanOperation Types

| Operation | Description | SQL Generation |
|-----------|-------------|----------------|
| SCAN | Read rows from a table | SELECT ... FROM table |
| FILTER | Apply WHERE conditions | WHERE condition |
| JOIN | Combine two tables | JOIN table ON condition |
| AGGREGATE | GROUP BY + aggregates | GROUP BY cols, SELECT aggs |
| WINDOW | Apply window functions | SELECT func() OVER (...) |
| SORT | Order rows | ORDER BY cols |
| LIMIT | Limit rows | LIMIT N |
| SUBQUERY_EXEC | Execute subquery | (SELECT ...) |
| UNION | Combine results | UNION / UNION ALL |
| PROJECT | Select/rename columns | SELECT cols |
| DISTINCT | Deduplicate | SELECT DISTINCT |
| CTE | Common table expression | WITH cte AS (...) |

### 9.3 Step Ordering (Topological Sort)

```
Given a set of PlanSteps with dependencies, compute execution order:

1. Build dependency graph: steps as nodes, dependency edges
2. Find all steps with zero dependencies -> level 0
3. Remove level 0 steps, update remaining dependencies
4. Find new zero-dependency steps -> level 1
5. Repeat until all steps ordered
6. If cycle detected: flag planning error, initiate reflection

Constraint: plan must be executable as a single SQL statement
  - If not possible (cross-DB, unsupported operations): split into multiple statements
  - Each statement becomes a separate PlanStep group
  - Groups connected by result-set merge operations
```

---

## 10. Planner Memory

### 10.1 What Is Remembered

The Planner maintains memory across reflection cycles and within a session:

| Memory Type | Scope | Content | Retention |
|-------------|-------|---------|-----------|
| **Plan State** | Single query | Current plan, validation errors, reflection count | Query lifecycle |
| **Sub-plan cache** | Single query | Validated sub-plans, intermediate results | Query lifecycle |
| **Decision trace** | Single query | Why each planning decision was made | Query lifecycle + debugging |
| **Session context** | User session | Recently resolved terms, preferred join paths | Session (30 min TTL) |
| **Learning signals** | Cross-query | Successful plan patterns, common corrections | Persistent (KE store) |

### 10.2 Memory Architecture

```
+------------------+
| Plan Memory       |
+------------------+
        |
        v
+------------------+     +------------------+
| Short-term        |     | Long-term         |
| (in-process)      |     | (KE query history)|
+------------------+     +------------------+
| - Current plan    |     | - Successful plans|
| - Validation errs |     | - Common joins   |
| - Decision trace  |     | - User patterns  |
| - Sub-plan cache  |     | - Feedback data  |
+------------------+     +------------------+
```

### 10.3 Reflection-Aware Memory

During reflection cycles:

```
Cycle 1: Build initial plan -> Validate -> Found errors
  -> Store: failing step ID, error type, validation context
  -> Recall: similar errors from session memory
  -> Re-plan: only the failing step (not full plan)

Cycle 2: Re-planned step -> Validate -> Still errors
  -> Store: second error context
  -> Recall: previously successful alternatives
  -> Re-plan: escalate to full re-plan (all steps)
  -> If still failing: emit current best-effort plan with error annotation
```

---

## 11. Tool Usage

### 11.1 Tools Available to the Planner

| Tool | Purpose | Input | Output | Cost |
|------|---------|-------|--------|------|
| **schema_lookup** | Get table/column metadata | table_name, column_name | Column type, nullable, PK, FK | < 5ms |
| **relationship_graph** | Find join paths | list of table IDs | Ordered join edges with confidence | < 20ms |
| **metric_resolve** | Resolve business metric to SQL | metric_name | Metric definition, formula, columns | < 100ms |
| **cost_estimate** | Estimate query step cost | table, filter, join type | Estimated rows, selectivity, cost | < 10ms |
| **term_resolve** | Map business term to schema | term, context | Table/column matches with confidence | < 50ms |
| **type_check** | Verify type compatibility | column, operation | Valid/invalid with reason | < 2ms |
| **decomposition_hint** | Ask LLM for decomposition | query, context | Sub-queries with goals | LLM call |
| **join_order_advice** | Ask LLM for join order | tables, relationships | Recommended order + rationale | LLM call |

### 11.2 Tool Selection Policy

| Planning Step | Primary Tool | Fallback Tool | Max Calls |
|---------------|-------------|---------------|-----------|
| Join path discovery | relationship_graph | schema_lookup + name matching | 5 |
| Column validation | schema_lookup | type_check | 20 |
| Metric resolution | metric_resolve | term_resolve | 3 |
| Term disambiguation | term_resolve | decomposition_hint (LLM) | 2 |
| Join order | cost_estimate | join_order_advice (LLM) | 2 |
| Decomposition | Heuristic rules | decomposition_hint (LLM) | 1 |

---

## 12. Cost Estimation

### 12.1 Estimation Model

```
For each plan step, estimate:

1. Input rows: estimated rows from upstream step (or table row count for base tables)
2. Selectivity: fraction of rows that pass filter
   - Equality filter on PK: selectivity = 1/table_rows (highly selective)
   - Equality filter on non-indexed column: selectivity = 0.1 (estimate)
   - Range filter (> , < , BETWEEN): selectivity = 0.3 (estimate)
   - Text search (LIKE, ILIKE): selectivity = 0.05 (estimate)
   - Multiple filters: product of individual selectivities
   - IN list: selectivity = list_size / distinct_values
   - OR conditions: sum of selectivities (capped at 1.0)
3. Output rows: input_rows * selectivity
4. Join cardinality:
   - INNER JOIN on PK-FK: output = max(left_rows, right_rows * selectivity)
   - LEFT JOIN: output = left_rows + (left_rows * right_matches / right_rows)
   - CROSS JOIN: output = left_rows * right_rows
5. Aggregation output: number of distinct GROUP BY combinations
6. Window function output: same as input rows (no row reduction)
7. Relative cost: output_rows * operation_cost_factor
   - SCAN: 1.0
   - FILTER: 0.5
   - JOIN (INNER): 2.0
   - JOIN (OUTER): 2.5
   - AGGREGATE: 1.5
   - WINDOW: 2.0
   - SORT: rows * log(rows) * 0.1
   - DISTINCT: 1.5
```

### 12.2 Estimation Accuracy Targets

| Plan Complexity | Row Count Accuracy | Cost Accuracy | Measurement |
|-----------------|-------------------|---------------|-------------|
| Simple (1-2 tables, no aggregates) | \u00b1 30% | \u00b1 20% | Compare to actual execution |
| Medium (3-5 tables, simple aggregates) | \u00b1 50% | \u00b1 35% | Compare to actual execution |
| Complex (6+ tables, windows, subqueries) | \u00b1 100% | \u00b1 50% | Compare to actual execution |
| Cross-database | Order of magnitude | \u00b1 100% | Compare to actual execution |

### 12.3 Cost Thresholds

| Threshold | Action |
|-----------|--------|
| Estimated rows > 1M | Flag as large result set, plan pagination |
| Estimated rows > 10M | Suggest aggregation or filtering |
| Estimated cost > 1000 | Warn user about query complexity |
| Cross-DB join estimated > 30s | Suggest user narrow criteria |
| Subquery depth > 3 | Flag as complex, suggest CTE |

---

## 13. Plan Validation

### 13.1 Validation Rules

| Rule | Check | Error Code | Severity |
|------|-------|------------|----------|
| Tables exist | All referenced tables exist in schema store | PLAN-001 | FATAL |
| Accessible | User has permission to query all tables | PLAN-002 | FATAL |
| Columns exist | All referenced columns exist in their tables | PLAN-003 | FATAL |
| Column-operator compatibility | Data types support planned operations | PLAN-004 | WARNING |
| Join paths valid | Join conditions reference real columns | PLAN-005 | FATAL |
| Join type compatible | No contradictory join conditions | PLAN-006 | WARNING |
| GROUP BY valid | GROUP BY columns exist in selected tables | PLAN-007 | FATAL |
| Aggregate function valid | Function is valid for column type | PLAN-008 | WARNING |
| Window frame valid | ORDER BY and frame specification compatible | PLAN-009 | WARNING |
| Subquery structure valid | Subquery returns appropriate row/column count | PLAN-010 | FATAL |
| Self-join alias | Self-joins have unique table aliases | PLAN-011 | WARNING |
| Circular dependency | No circular dependencies between plan steps | PLAN-012 | FATAL |
| Cross-DB capability | Cross-DB operations are supported | PLAN-013 | WARNING |
| Cost within limits | Estimated cost below user/tenant threshold | PLAN-014 | WARNING |

### 13.2 Validation Order

```
1. Structural validation (tables, columns, types exist)
   - Fastest checks, catch most common errors
   - No external calls needed (schema store query cached)

2. Semantic validation (join paths, grouping, aggregates)
   - Medium-cost checks
   - Uses relationship graph and type system

3. Cost validation (estimate within thresholds)
   - Most expensive check (requires cost estimation)
   - Only run if structural + semantic validation pass
```

### 13.3 Validation Result

```
ValidationResult {
    valid: bool
    errors: [ValidationError {
        step_id: UUID
        rule: string
        code: string
        severity: "FATAL" | "WARNING"
        message: string
        suggestion: string | null      // How to fix
        affected_columns: [ColumnRef]
    }]
    warnings: [ValidationWarning]
    metadata: {
        validation_time_ms: int
        rules_checked: int
        rules_passed: int
        rules_failed: int
    }
}
```

---

## 14. Reflection Loop

### 14.1 When to Reflect

| Condition | Action | Max Cycles |
|-----------|--------|------------|
| FATAL validation errors | Re-plan failing steps | 2 |
| WARNING validation errors | Continue with warnings, log | 0 (warnings propagated) |
| Cost exceeds threshold | Suggest optimization, accept plan | 1 (optimization attempt) |
| Empty result expected | Verify plan correctness | 0 (flag to user) |
| Ambiguous join path | Ask LLM for join selection | 2 |

### 14.2 Reflection Flow

```
Plan Built
    |
    v
Validate
    |
    +-- PASS -> Emit QueryPlan to Generator
    |
    +-- FAIL (FATAL) -> Reflection cycle
         |
         +-- Identify failing step
         +-- Analyze error type
         +-- Check error memory (previous cycles)
         +-- Determine correction strategy:
         |     - Missing table: add table, re-validate
         |     - Missing column: suggest alternative column
         |     - Invalid join: try alternative join path
         |     - Invalid aggregate: change function type
         |     - Invalid group by: add column to GROUP BY
         |     - Circular dependency: re-order steps
         +-- Apply correction -> Re-validate
         |
         +-- Cycle 1 still fails -> Try alternative strategy
         |     - Full re-plan instead of step-level fix
         |     - Use LLM assistance for ambiguous decisions
         |
         +-- Cycle 2 still fails -> Escalate
               - Emit best-effort plan with error annotations
               - Flag for Repair Agent (AI-Agent-Spec.md \u00a78)
```

### 14.3 Correction Strategies by Error

| Error Pattern | Primary Correction | Secondary Correction |
|--------------|-------------------|---------------------|
| Table not found | Search for similar table names | Remove table reference if optional |
| Column not found | Search for similar column names | Check if column was renamed |
| Invalid join path | Try alternative FK relationship | Try name-based join |
| Aggregate type mismatch | Convert to compatible aggregate | Suggest alternate aggregation |
| Invalid GROUP BY | Add missing columns to GROUP BY | Change to non-aggregate query |
| Subquery returns multiple rows | Add LIMIT 1 or convert to IN | Restructure as JOIN |
| Cross-DB not supported | Plan result-set merge | Flag as not supported |

---

## 15. Failure Recovery

### 15.1 Failure Modes

| Failure Mode | Detection | Recovery Strategy |
|-------------|-----------|-------------------|
| **Schema store unavailable** | Connection timeout on schema_lookup | Use cached schema (stale but available) |
| **Relationship graph unavailable** | Timeout on relationship_graph | Fall back to name-based join detection |
| **LLM tool call fails** | HTTP error from LLM | Use rule-based fallback, accept lower quality |
| **Cost estimator timeout** | Estimation exceeds 100ms | Use default estimates (pessimistic) |
| **Validation timeout** | Validation exceeds 500ms | Accept partial validation (structural only) |
| **Memory limit reached** | In-process memory > 100MB | Drop session memory, keep only current plan |
| **Reflection cycle maxed** | 2 cycles completed | Emit best-effort plan with error annotations |
| **Unknown query type** | Intent confidence < 0.5 | Return error: unable to interpret query |

### 15.2 Degraded Mode Behavior

| Degraded State | Behavior | Output Quality |
|----------------|----------|---------------|
| Schema store stale | Use cached schema (may miss new columns) | Join discovery may miss recent changes |
| LLM unavailable | Rule-based planning only | Fails on ambiguous or complex queries |
| Relationship graph stale | Name-based join detection only | Missing inferred relationships |
| Cost estimator degraded | Pessimistic default estimates | May choose suboptimal join order |
| No decomposition (LLM needed) | Treat as single query | Fails on compound questions |
| Memory full | Clear session memory, restart planning | No cross-query learning |

### 15.3 Recovery Time Objectives

| Failure | RTO | RPO |
|---------|-----|-----|
| Schema store unavailable | < 5s (failover) | 0 (cached data) |
| Relationship graph unavailable | < 5s (retry) | 0 (cached relationships) |
| LLM tool failure | < 2s (fallback) | N/A (no data loss) |
| Planner crash | < 10s (restart) | < 100ms (in-flight plan loss) |

---

## 16. Retry Policy

### 16.1 Retry Configuration

| Operation | Max Retries | Backoff | Timeout |
|-----------|-------------|---------|---------|
| schema_lookup | 2 | 100ms, 500ms | 2s |
| relationship_graph | 2 | 200ms, 1s | 5s |
| metric_resolve | 1 | 500ms | 3s |
| term_resolve | 2 | 200ms, 1s | 3s |
| cost_estimate | 1 | 100ms | 1s |
| type_check | 0 | N/A | 500ms |
| LLM tool call | 2 | 1s, 5s | 15s |
| Plan validation | 0 | N/A | 5s |

### 16.2 Overall Planner Time Budget

| Query Complexity | Total Time Budget | Planning | Validation | Reflection |
|-----------------|-------------------|----------|------------|------------|
| Simple | 2s | 1s | 0.5s | 0.5s |
| Medium | 5s | 3s | 1s | 1s |
| Complex | 15s | 8s | 3s | 4s |
| Very Complex | 30s | 15s | 5s | 10s |

---

## 17. State Machine

### 17.1 Planner State Machine

```
                    +------------------+
                    |    INITIALIZED    |
                    | Plan requested,   |
                    | context loaded    |
                    +--------+---------+
                             |
                             v
                    +------------------+
        +---------->| INTENT_CLASSIFY  |<---------+
        |           | Determine query   |          |
        |           | type and scope    |          |
        |           +--------+---------+          |
        |                    |                     |
        |                    v                     |
        |           +------------------+          |
        |        +->| DECOMPOSE        |          |
        |        |  | Break into        |          |
        |        |  | sub-queries       |          |
        |        |  +--------+---------+          |
        |        |           |                     |
        |        |           v                     |
        |        |  +------------------+          |
        |        |  | PLAN_JOINS       |          |
        |        |  | Discover paths,   |          |
        |        |  | select types      |          |
        |        |  +--------+---------+          |
        |        |           |                     |
        |        |           v                     |
        |        |  +------------------+          |
        |        |  | PLAN_AGGREGATION |          |
        |        |  | Group, functions, |          |
        |        |  | HAVING            |          |
        |        |  +--------+---------+          |
        |        |           |                     |
        |        |           v                     |
        |        |  +------------------+          |
        |        |  | PLAN_WINDOW      |          |
        |        |  | Window functions  |          |
        |        |  +--------+---------+          |
        |        |           |                     |
        |        |           v                     |
        |        |  +------------------+          |
        |        |  | PLAN_SUBQUERY    |          |
        |        |  | Nested queries    |          |
        |        |  +--------+---------+          |
        |        |           |                     |
        |        |           v                     |
        |        |  +------------------+          |
        |        |  | ESTIMATE_COST    |          |
        |        |  | Row counts,       |          |
        |        |  | selectivity       |          |
        |        |  +--------+---------+          |
        |        |           |                     |
        |        |           v                     |
        |        |  +------------------+          |
        |        |  | VALIDATE_PLAN    |          |
        |        |  | Structural,       |          |
        |        |  | semantic, cost    |          |
        |        |  +--------+---------+          |
        |        |        |         |              |
        |        |    VALID    INVALID             |
        |        |        |         |              |
        |        |        v         v              |
        |        |  +----------+  +----------+    |
        |        |  | BUILD    |  | REFLECT  |----+
        |        |  | PLAN     |  | Identify  |
        |        |  +----------+  | error,    |
        |        |       |        | correct   |
        |        |       v        +----------+    |
        |        |  +----------+                  |
        |        |  | COMPLETE |                  |
        |        |  +----------+                  |
        |        |                                |
        +--------+--------------------------------+
                 (max 2 reflection cycles)
```

### 17.2 State Transitions

| Current State | Event | Next State | Guard Condition |
|---------------|-------|------------|-----------------|
| INITIALIZED | Context loaded | INTENT_CLASSIFY | Context contains \u2265 1 table |
| INTENT_CLASSIFY | Type determined | DECOMPOSE | Confidence \u2265 0.8 |
| INTENT_CLASSIFY | Type ambiguous | Complete with ERROR | Confidence < 0.5 |
| DECOMPOSE | Sub-queries identified | PLAN_JOINS | All sub-queries validated |
| DECOMPOSE | No decomposition needed | PLAN_JOINS | Single sub-query |
| PLAN_JOINS | Join paths selected | PLAN_AGGREGATION | Query contains aggregation |
| PLAN_JOINS | Join paths selected | PLAN_WINDOW | Query contains window functions |
| PLAN_JOINS | No aggregation/window | ESTIMATE_COST | Simple SELECT |
| PLAN_AGGREGATION | Aggregation planned | PLAN_WINDOW | Query also has window functions |
| PLAN_AGGREGATION | Aggregation planned | PLAN_SUBQUERY | Query also has subqueries |
| PLAN_AGGREGATION | Aggregation done | ESTIMATE_COST | No more operations to plan |
| PLAN_WINDOW | Window planned | PLAN_SUBQUERY | Query also has subqueries |
| PLAN_WINDOW | Window done | ESTIMATE_COST | No more operations |
| PLAN_SUBQUERY | Subqueries planned | ESTIMATE_COST | All operations planned |
| ESTIMATE_COST | Cost estimated | VALIDATE_PLAN | Estimate complete |
| VALIDATE_PLAN | All valid | BUILD_PLAN | No FATAL errors |
| VALIDATE_PLAN | FATAL errors found | REFLECT | reflection_count < 2 |
| VALIDATE_PLAN | FATAL errors persist | COMPLETE_WITH_WARNINGS | reflection_count \u2265 2 |
| REFLECT | Correction applied | INTENT_CLASSIFY | Full re-plan needed |
| REFLECT | Correction applied | PLAN_JOINS | Step-level fix |

### 17.3 Error States

| State | Meaning | Recovery |
|-------|---------|----------|
| INTENT_CLASSIFY_FAILED | Cannot determine query type | Return error to user |
| DECOMPOSE_FAILED | Cannot decompose compound query | Treat as single query with warning |
| PLAN_JOINS_FAILED | No valid join paths found | Flag partial plan, suggest manual joins |
| PLAN_AGGREGATION_FAILED | Invalid aggregation structure | Simplify to non-aggregate query |
| PLAN_WINDOW_FAILED | Invalid window specification | Remove window functions |
| PLAN_SUBQUERY_FAILED | Subquery cannot be planned | Suggest user simplify |
| COST_ESTIMATE_FAILED | Estimation error | Use pessimistic defaults |
| VALIDATE_FAILED | Structural validation error | Cannot recover, return error |
| REFLECT_MAXED | Max reflection cycles reached | Emit best-effort with error annotations |
| TIMEOUT | Planning exceeded time budget | Return partial plan or timeout error |

---

## 18. Metrics

### 18.1 Key Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|----------------|
| planner_queries_total | Counter | Total queries planned | - |
| planner_queries_by_type | Counter | Queries by type (SIMPLE, JOIN, AGG, etc.) | - |
| planner_queries_by_complexity | Counter | Queries by complexity level | - |
| planner_duration_seconds | Histogram | End-to-end planning time | P95 > budget |
| planner_step_duration | Histogram | Duration per planning step | P95 > 2s |
| planner_validation_duration | Histogram | Validation time | P95 > 1s |
| planner_reflection_count | Histogram | Reflection cycles per query | > 2 is error |
| planner_reflection_reason | Counter | Why reflection was triggered | Track patterns |
| planner_errors_total | Counter | Planning errors by type | > 5% of queries |
| planner_validation_errors | Counter | Validation errors by code | Track by code |
| planner_decomposition_count | Histogram | Sub-queries per compound query | - |
| planner_join_count | Histogram | Joins per query | - |
| planner_estimated_rows | Histogram | Estimated result rows | - |
| planner_estimated_cost | Histogram | Estimated query cost | - |
| planner_tool_calls | Counter | Tool call count per query | - |
| planner_cost_estimate_accuracy | Gauge | |estimated - actual| / actual | < 50% target |
| planner_memory_usage_bytes | Gauge | In-process memory | > 100MB alert |
| planner_cache_hit_ratio | Gauge | Sub-plan cache hit rate | < 10% suggests cache issue |
| planner_intent_accuracy | Gauge | Intent classification accuracy | Monitored via feedback |

### 18.2 Dashboards

```
Dashboard: Planner Health
  - Planning duration (P50/P95/P99) over time
  - Queries by type (stacked area)
  - Reflection rate (% of queries needing reflection)
  - Validation error rate by code
  - Tool call distribution
  - Memory usage

Dashboard: Plan Quality
  - Cost estimate accuracy (ratio of estimated to actual)
  - Decomposition count distribution
  - Join count distribution
  - Reflection reason breakdown
  - Intent classification accuracy (from feedback)
```

### 18.3 Traces

Every planning operation emits OpenTelemetry spans:

```
Span: planner.plan
  Span: planner.intent_classify
  Span: planner.decompose
  Span: planner.plan_joins
    Span: planner.relationship_graph_lookup
    Span: planner.join_order_select
  Span: planner.plan_aggregation
  Span: planner.plan_window
  Span: planner.plan_subquery
  Span: planner.estimate_cost
  Span: planner.validate
    Span: planner.validate.structural
    Span: planner.validate.semantic
    Span: planner.validate.cost
  Span: planner.reflect (if applicable)
    Span: planner.reflect.analyze_error
    Span: planner.reflect.apply_correction
```

---

## 19. Performance Targets

### 19.1 Latency Budgets

| Operation | P50 | P95 | P99 | Measurement |
|-----------|-----|-----|-----|-------------|
| Intent classification | 50ms | 100ms | 200ms | Timer from input to classification |
| Query decomposition | 100ms | 300ms | 500ms | Timer for compound queries only |
| Join planning (2 tables) | 50ms | 100ms | 200ms | Timer for 1 join |
| Join planning (5 tables) | 200ms | 500ms | 1s | Timer for 4 joins |
| Join planning (10 tables) | 500ms | 1s | 2s | Timer for 9 joins |
| Aggregation planning | 100ms | 200ms | 500ms | Timer |
| Window function planning | 50ms | 100ms | 200ms | Timer |
| Subquery planning | 100ms | 300ms | 500ms | Timer |
| Cost estimation | 50ms | 100ms | 200ms | Timer |
| Plan validation | 100ms | 300ms | 500ms | Timer |
| Full plan (simple query) | 300ms | 500ms | 1s | End-to-end |
| Full plan (medium query) | 1s | 2s | 5s | End-to-end |
| Full plan (complex query) | 3s | 8s | 15s | End-to-end |
| Full plan (cross-DB) | 5s | 15s | 30s | End-to-end |
| Tool call (schema_lookup) | 5ms | 10ms | 20ms | Per call |
| Tool call (relationship_graph) | 10ms | 30ms | 50ms | Per call |
| Tool call (LLM) | 500ms | 2s | 5s | Per call |

### 19.2 Throughput Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Plans per second (simple) | 50 | Plans generated per second |
| Plans per second (mixed workload) | 20 | Plans generated per second |
| Concurrent planning sessions | 100 | In-flight planning operations |
| Tool calls per plan (simple) | < 5 | Average tool calls |
| Tool calls per plan (complex) | < 20 | Average tool calls |
| Reflection rate | < 15% of queries | Percentage needing \u2265 1 cycle |
| Validation pass rate (first attempt) | > 80% | Percentage passing on first validation |

### 19.3 Resource Budgets

| Resource | Per Query | Burst | Notes |
|----------|-----------|-------|-------|
| CPU | 200ms (simple) - 5s (complex) | 10 concurrent | Stateless, horizontally scalable |
| Memory | 10MB (simple) - 100MB (complex) | 2GB total | Plan memory freed after emission |
| Network | 10-50 tool calls | 50 req/s | Mostly KE API calls |
| LLM tokens | 0 (simple) - 500 (complex) | 2000 tok/min | Only for ambiguous cases |

---

## 20. APIs

### 20.1 Internal Planner API (Port 8400, Internal)

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| /v1/plan | POST | Generate query plan | Query + Context | QueryPlan |
| /v1/plan/validate | POST | Validate an existing plan | QueryPlan | ValidationResult |
| /v1/plan/estimate | POST | Estimate cost of a plan | QueryPlan | CostEstimate |
| /v1/plan/decompose | POST | Decompose a compound query | Query | [SubQuery] |
| /v1/plan/joins | POST | Plan joins for tables | [TableRef] | JoinPlan |
| /v1/plan/intent | POST | Classify query intent | Query | QueryIntent |
| /v1/plan/status/{plan_id} | GET | Get plan status | - | PlanStatus |
| /v1/plan/health | GET | Health check | - | { status, components } |

### 20.2 Event API

| Event | Emitter | Payload | Subscribers |
|-------|---------|---------|-------------|
| plan.created | Planner | { plan_id, query_intent, complexity } | Tracing, metrics |
| plan.completed | Planner | { plan_id, duration_ms, reflection_count, steps } | Generator |
| plan.failed | Planner | { plan_id, error_code, reason } | Alerting, metrics |
| plan.reflection | Planner | { plan_id, cycle, error_code, correction } | Metrics, debugging |
| plan.validation_failed | Planner | { plan_id, errors[], warnings[] } | Reflection controller |
| plan.cost_high | Planner | { plan_id, estimated_cost, threshold } | Policy enforcement stack |

---

## 21. Testing

### 21.1 Test Levels

| Level | Scope | Framework | Coverage Target |
|-------|-------|-----------|----------------|
| **Unit** | Intent classifier, decomposition rules, validation rules | pytest | > 90% line |
| **Integration** | Join planning with real KE, full pipeline end-to-end | pytest + testcontainers | > 80% path |
| **E2E** | Full plan cycle (input \u2192 QueryPlan output) | pytest | All 10 query types |
| **Performance** | Latency budgets, throughput targets | k6 | P50/P95 within budget |
| **Regression** | Known query patterns produce correct plans | pytest | 100% of regression suite |

### 21.2 Test Scenarios

```
Intent Classification Tests:
  - classify_simple_select: "Show all customers" -> SIMPLE_SELECT
  - classify_filtered_select: "Orders from last month" -> FILTERED_SELECT
  - classify_join: "Orders with customer names" -> JOIN
  - classify_aggregation: "Total sales by region" -> AGGREGATION
  - classify_compound: "Products with above-average sales" -> COMPOUND
  - classify_window: "Rank employees by salary" -> WINDOW
  - classify_subquery: "Customers who placed > 5 orders" -> SUBQUERY
  - classify_cross_db: "Compare sales across databases" -> CROSS_DB
  - classify_ambiguous: Low confidence -> LLM fallback
  - classify_ddl: "Create a view" -> REJECT

Decomposition Tests:
  - decompose_compound_and: Two independent sub-queries
  - decompose_comparative: Q1 vs Q2 comparison
  - decompose_conditional: Inner + outer sub-query
  - decompose_multi_step: Growth rate calculation chain
  - decompose_cross_db: Per-database sub-queries
  - decompose_single: No decomposition needed

Join Planning Tests:
  - join_explicit_fk: Known FK relationship -> INNER JOIN
  - join_inferred_fk: Name-based FK -> INNER JOIN with confidence
  - join_optional: Nullable FK -> LEFT JOIN
  - join_self: Self-referencing table -> Self-JOIN with alias
  - join_cross_db: Tables from different databases -> Cross-DB plan
  - join_no_relationship: Unknown relationship -> Cross-JOIN warning
  - join_three_tables: 3-table join path

Aggregation Planning Tests:
  - aggregate_simple_group_by: "Total sales by region"
  - aggregate_multi_agg: "Count and average by category"
  - aggregate_having: "Regions with sales > 1M"
  - aggregate_complex_rollup: Multi-level grouping
  - aggregate_no_group_by: "Total sales" (single value)

Window Function Tests:
  - window_rank: "Rank products by sales"
  - window_row_number: "Top 5 by category" (PARTITION BY)
  - window_running_total: "Running total by month"
  - window_moving_avg: "Moving average, 3-month window"
  - window_lag_lead: "Previous month comparison"

Cost Estimation Tests:
  - cost_simple_select: Single table, no filter
  - cost_filtered_select: Selective filter on PK
  - cost_multi_join: 5-table join chain
  - cost_large_aggregation: GROUP BY on 10M row table
  - cost_cross_db: Cross-DB estimation

Validation Tests:
  - validate_correct_plan: All rules pass
  - validate_missing_table: FATAL error PLAN-001
  - validate_missing_column: FATAL error PLAN-003
  - validate_type_mismatch: WARNING error PLAN-004
  - validate_invalid_join: FATAL error PLAN-005
  - validate_circular_dependency: FATAL error PLAN-012
  - validate_cost_exceeded: WARNING error PLAN-014

Reflection Tests:
  - reflect_single_cycle: Error corrected on first cycle
  - reflect_two_cycles: Error corrected on second cycle
  - reflect_max_cycles: Max cycles reached, emits best-effort
  - reflect_no_correction: Error cannot be corrected
  - reflect_memory: Previous error context used in correction

End-to-End Tests:
  - e2e_simple_select: input -> plan -> expected plan structure
  - e2e_multi_join: 5-table join -> expected join order
  - e2e_compound_decompose: Compound query -> sub-plans
  - e2e_cross_db: Cross-DB query -> merge plan
  - e2e_complex_analytical: Full analytical pipeline
```

### 21.3 Test Data Requirements

| Dataset | Type | Tables | Purpose |
|---------|------|--------|---------|
| Northwind | PostgreSQL | 13 | Standard join patterns |
| AdventureWorks | SQL Server | 70+ | Complex schemas, many joins |
| TPC-H | PostgreSQL | 8 | Analytical queries, aggregations |
| TPC-DS | PostgreSQL | 24 | Decision support, complex operations |
| Cross-DB (PG + MySQL) | Mixed | 6 each | Cross-database planning |
| Self-referencing | Custom | 3 | Org charts, category trees |
| Large schema | Custom | 500 | Performance testing |

### 21.4 Acceptance Criteria

- [ ] All 10 query types produce correct plans
- [ ] Decomposition produces correct sub-query dependency order
- [ ] Join planning discovers all valid join paths for test datasets
- [ ] Aggregation planning produces correct GROUP BY + aggregate sets
- [ ] Window function planning produces correct OVER() specifications
- [ ] Subquery planning correctly identifies correlation
- [ ] Cost estimation within \u00b1 50% for simple queries
- [ ] Validation catches all FATAL errors before plan emission
- [ ] Reflection loop resolves > 80% of FATAL errors within 2 cycles
- [ ] End-to-end planning latency within P50/P95 budgets
- [ ] No false negatives in validation (valid plan rejected)

---

## 22. Future Extensibility

### 22.1 Post-MVP Enhancements

| Enhancement | Value | Complexity | Timeline |
|-------------|-------|------------|----------|
| ML-based cost estimation | More accurate plan selection | High | Month 6 |
| Learned join order from query history | Better join order for common patterns | Medium | Month 4 |
| Automated plan alternative generation | Explore N plan candidates, pick best | High | Month 8 |
| Recursive CTE planning | Support hierarchical queries | Medium | Month 5 |
| PIVOT/UNPIVOT planning | Cross-tabulation queries | Medium | Month 7 |
| Fuzzy table/column matching | Handle typos in user queries | Low | Month 3 |
| Plan visualization for admin UI | Debugging and transparency | Low | Month 3 |
| Multi-statement transaction planning | Sequence of dependent statements | High | Month 10 |
| User preference learning | Learn preferred join paths per user | Medium | Month 6 |
| Plan explanation generation | Explain "why this plan" to users | Medium | Month 5 |

### 22.2 Extensibility Points

| Extension Point | Interface | Example |
|----------------|-----------|---------|
| Custom join order strategy | JoinOrderStrategy interface | "Always prefer indexed columns" |
| Custom cost model | CostModel interface | "Weight network cost higher" |
| Custom validation rule | ValidationRule interface | "Reject queries on stale tables" |
| Custom decomposition strategy | DecompositionStrategy interface | "Always decompose cross-DB" |
| Custom intent classifier | IntentClassifier interface | "Domain-specific query types" |

---

## Appendix A: Cross-References

| Planner Component | Related Document | Relationship |
|-------------------|-----------------|--------------|
| Intent classification | AI-Agent-Specification.md \u00a74.2 | Planner feeds intent to Generator |
| Join planning | Schema-Specification.md \u00a76 | Relationship graph from Schema Intelligence |
| Metric resolution | KnowledgeEngine-Specification.md \u00a76 | Business metric definitions from KE |
| Plan output | AI-Agent-Specification.md \u00a75.3 | Generator consumes QueryPlan |
| Plan validation | AI-Agent-Specification.md \u00a76 | Validator checks plan before SQL gen |
| Reflection loop | AI-Agent-Specification.md \u00a77.4 | Planner reflection feeds Repair Agent |
| Cost estimation | Performance-Specification.md \u00a74 | Cost model consistent with per-query cost |
| Latency budgets | Performance-Specification.md \u00a71 | Planning latency part of E2E budget |
| Model routing | Performance-Specification.md \u00a75 | Complexity classification feeds router |
| Plan events | API-Specification.md \u00a79 | Plan events on event bus |
| Query decomposition | API-Specification.md \u00a78.3 | Sub-query tracking via job IDs |
| Metadata lookup | Database-Specification.md \u00a75 | Schema store for table/column validation |

## Appendix B: Risks and Assumptions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Intent misclassification leads to wrong plan structure | Medium | High | Confidence thresholds, LLM fallback, user confirmation |
| Join path discovery fails for denormalized schemas | Medium | Medium | Name-based fallback, query history mining |
| Cost estimation errors lead to poor join order | Medium | Medium | Multiple join order candidates, LLM-assisted selection |
| Decomposition creates incorrect sub-query dependencies | Low | High | Dependency validation, reflection recovery |
| Reflection loop fails to correct persistent errors | Low | Medium | Max cycle limit, best-effort emission, Repair Agent |
| LLM tool calls introduce latency spikes | Medium | Medium | Timeout, fallback to rule-based, LLM call budget |

### Assumptions

| Assumption | Impact if Wrong | Validation |
|------------|----------------|------------|
| Schema store contains current metadata | Validation may use stale info | Validated by sync cycle frequency |
| Relationship graph has reasonable FK coverage | Join discovery quality degrades | Research spike EP-017 validates on enterprise data |
| Most enterprise queries use \u2264 5 tables | Complex query planning may be under-tested | Production monitoring after launch |
| Intent can be classified without full understanding | Ambiguous queries misclassified | LLM fallback provides safety net |
| Decomposition is beneficial for < 20% of queries | Decomposition overhead unnecessary for simple queries | Performance monitoring, skip decomposition when not needed |

## Appendix C: Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-10 | Principal AI Planning Architect | Initial specification \u2014 22 sections covering complete Query Planning subsystem |

---
*End of Planner-Specification.md*
