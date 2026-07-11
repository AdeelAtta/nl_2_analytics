"""
Load testing script for the query pipeline.

Usage:
    # Quick smoke test (10 queries)
    python -c "import asyncio; from ke.benchmark.load_test import run_load_test; asyncio.run(run_load_test(concurrent=2, total=10))"

    # Heavy load test
    python -c "import asyncio; from ke.benchmark.load_test import run_load_test; asyncio.run(run_load_test(concurrent=10, total=100))"
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from ke.services.pipeline import PipelineOrchestrator

TEST_QUERIES = [
    "show me active users",
    "list all products",
    "total revenue by quarter",
    "orders from last month",
    "find customers from new york",
    "top 5 most expensive products",
    "how many employees",
    "list products out of stock",
    "show me all customers",
    "total sales by category",
    "employees by salary",
    "monthly revenue trend",
    "users who signed up last week",
    "product inventory by warehouse",
]


async def run_single_query(
    orch: PipelineOrchestrator,
    query: str,
    idx: int,
) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        result = await orch.execute(query=query, tenant_id="loadtest", dry_run=True)
        elapsed = (time.perf_counter() - start) * 1000
        return {
            "idx": idx, "query": query, "status": result.status.value,
            "latency_ms": round(elapsed, 1), "sql": result.sql,
            "error": result.error,
        }
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return {
            "idx": idx, "query": query, "status": "error",
            "latency_ms": round(elapsed, 1), "sql": "", "error": str(e),
        }


async def run_load_test(concurrent: int = 5, total: int = 50) -> dict[str, Any]:
    print(f"Load test: {total} queries, {concurrent} concurrent")
    print("-" * 60)

    orch = PipelineOrchestrator()
    semaphore = asyncio.Semaphore(concurrent)

    async def bounded(q: str, i: int) -> dict[str, Any]:
        async with semaphore:
            return await run_single_query(orch, q, i)

    tasks = []
    for i in range(total):
        q = TEST_QUERIES[i % len(TEST_QUERIES)]
        tasks.append(bounded(q, i))

    start = time.perf_counter()
    results = await asyncio.gather(*tasks)
    total_elapsed = (time.perf_counter() - start) * 1000

    latencies = [r["latency_ms"] for r in results]
    latencies.sort()
    errors = [r for r in results if r["status"] == "error"]
    successes = [r for r in results if r["status"] == "success"]

    summary = {
        "total": total,
        "concurrent": concurrent,
        "total_duration_ms": round(total_elapsed, 1),
        "throughput_qps": round(total / (total_elapsed / 1000), 1),
        "successful": len(successes),
        "errors": len(errors),
        "avg_latency_ms": round(sum(latencies) / max(len(latencies), 1), 1),
        "p50_ms": round(latencies[len(latencies) // 2], 1) if latencies else 0,
        "p95_ms": round(latencies[int(len(latencies) * 0.95)], 1) if latencies else 0,
        "p99_ms": round(latencies[int(len(latencies) * 0.99)], 1) if latencies else 0,
        "min_ms": round(latencies[0], 1) if latencies else 0,
        "max_ms": round(latencies[-1], 1) if latencies else 0,
    }

    print(f"\nResults:")
    print(f"  Total: {summary['total']} queries")
    print(f"  Concurrent: {summary['concurrent']}")
    print(f"  Duration: {summary['total_duration_ms']}ms")
    print(f"  Throughput: {summary['throughput_qps']} qps")
    print(f"  Successful: {summary['successful']}")
    print(f"  Errors: {summary['errors']}")
    print(f"  Latency:")
    print(f"    Avg: {summary['avg_latency_ms']}ms")
    print(f"    P50: {summary['p50_ms']}ms")
    print(f"    P95: {summary['p95_ms']}ms")
    print(f"    P99: {summary['p99_ms']}ms")
    print(f"    Min: {summary['min_ms']}ms")
    print(f"    Max: {summary['max_ms']}ms")

    return summary


if __name__ == "__main__":
    asyncio.run(run_load_test(concurrent=5, total=50))
