from __future__ import annotations

from typing import Any

BenchmarkQuery = dict[str, Any]

BENCHMARK_SUITE: list[BenchmarkQuery] = [
    {
        "id": "SIMPLE-001",
        "query": "show me active users",
        "complexity": "simple",
        "expected_patterns": ["users", "status", "active"],
        "expected_tables": ["users"],
        "description": "Simple filter on user status",
    },
    {
        "id": "SIMPLE-002",
        "query": "list all products",
        "complexity": "simple",
        "expected_patterns": ["products", "SELECT"],
        "expected_tables": ["products"],
        "description": "Simple select from products",
    },
    {
        "id": "SIMPLE-003",
        "query": "find customers from new york",
        "complexity": "simple",
        "expected_patterns": ["customers", "city", "new york"],
        "expected_tables": ["customers"],
        "description": "Filter by city",
    },
    {
        "id": "AGG-001",
        "query": "total revenue by quarter",
        "complexity": "aggregation",
        "expected_patterns": ["revenue", "SUM", "GROUP BY", "quarter"],
        "expected_tables": ["revenue"],
        "description": "Aggregation with group by",
    },
    {
        "id": "AGG-002",
        "query": "how many employees in each department",
        "complexity": "aggregation",
        "expected_patterns": ["employees", "COUNT", "GROUP BY"],
        "expected_tables": ["employees"],
        "description": "Count with group by",
    },
    {
        "id": "FILTER-001",
        "query": "orders placed last month",
        "complexity": "filter",
        "expected_patterns": ["orders", "date"],
        "expected_tables": ["orders"],
        "description": "Date filter on orders",
    },
    {
        "id": "FILTER-002",
        "query": "products that are out of stock",
        "complexity": "filter",
        "expected_patterns": ["products", "stock", "quantity", "0"],
        "expected_tables": ["products"],
        "description": "Stock filter",
    },
    {
        "id": "JOIN-001",
        "query": "top 10 customers by order volume",
        "complexity": "join",
        "expected_patterns": ["customers", "orders"],
        "expected_tables": ["customers", "orders"],
        "description": "Join customers with orders",
    },
    {
        "id": "JOIN-002",
        "query": "total sales by product category",
        "complexity": "join",
        "expected_patterns": ["products", "categories"],
        "expected_tables": ["products", "categories"],
        "description": "Join products with categories",
    },
    {
        "id": "SORT-001",
        "query": "top 5 most expensive products",
        "complexity": "sort",
        "expected_patterns": ["products", "ORDER BY", "price", "DESC"],
        "expected_tables": ["products"],
        "description": "Sort with limit",
    },
    {
        "id": "SORT-002",
        "query": "list employees by salary highest first",
        "complexity": "sort",
        "expected_patterns": ["employees", "ORDER BY", "salary", "DESC"],
        "expected_tables": ["employees"],
        "description": "Sort employees by salary descending",
    },
    {
        "id": "COMPLEX-001",
        "query": "monthly revenue trend for this year",
        "complexity": "complex",
        "expected_patterns": ["revenue", "date", "month"],
        "expected_tables": ["revenue"],
        "description": "Time-based trend query",
    },
]
