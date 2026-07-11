from __future__ import annotations

import time
from typing import Any

from ke.benchmark.queries import BENCHMARK_SUITE, BenchmarkQuery
from ke.services.demo_data import DEMO_TABLES, DEMO_COLUMNS, DEMO_RELATIONSHIPS
from ke.services.intent import IntentAgent
from ke.services.pipeline import PipelineOrchestrator


def score_sql_accuracy(generated_sql: str, expected: BenchmarkQuery) -> dict[str, Any]:
    sql_lower = generated_sql.lower()
    patterns_found = 0
    patterns_total = len(expected.get("expected_patterns", []))
    for pat in expected.get("expected_patterns", []):
        if pat.lower() in sql_lower:
            patterns_found += 1

    tables_found = 0
    tables_total = len(expected.get("expected_tables", []))
    for tbl in expected.get("expected_tables", []):
        if tbl.lower() in sql_lower:
            tables_found += 1

    has_select = "select" in sql_lower
    has_semicolon = generated_sql.strip().endswith(";")

    pattern_score = patterns_found / max(patterns_total, 1)
    table_score = tables_found / max(tables_total, 1)
    syntax_score = 1.0 if has_select else 0.0
    style_score = 0.5 if has_semicolon else 0.0

    overall = round(0.35 * pattern_score + 0.35 * table_score + 0.2 * syntax_score + 0.1 * style_score, 4)

    return {
        "overall": overall,
        "pattern_score": pattern_score,
        "table_score": table_score,
        "syntax_score": syntax_score,
        "style_score": style_score,
        "patterns_found": patterns_found,
        "patterns_total": patterns_total,
        "tables_found": tables_found,
        "tables_total": tables_total,
    }


async def run_benchmark(
    orchestrator: PipelineOrchestrator | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    if orchestrator is None:
        orchestrator = PipelineOrchestrator()

    results: list[dict[str, Any]] = []
    total_start = time.perf_counter()
    passed = 0
    failed = 0

    if verbose:
        print(f"{'ID':<15} {'Status':<8} {'Score':<8} {'SQL'}")
        print("-" * 80)

    for q in BENCHMARK_SUITE:
        start = time.perf_counter()
        try:
            result = await orchestrator.execute(query=q["query"], tenant_id="benchmark", dry_run=True)
            elapsed = (time.perf_counter() - start) * 1000
            score_data = score_sql_accuracy(result.sql or "", q)
            score_data["latency_ms"] = round(elapsed, 1)
            score_data["sql"] = result.sql
            score_data["id"] = q["id"]
            score_data["query"] = q["query"]

            status = "PASS" if score_data["overall"] >= 0.5 else "WARN" if score_data["overall"] >= 0.3 else "FAIL"
            if status == "PASS":
                passed += 1
            else:
                failed += 1

            results.append(score_data)

            if verbose:
                print(f"{q['id']:<15} {status:<8} {score_data['overall']:<8.3f} {(result.sql or 'N/A')[:50]}")
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            results.append({
                "id": q["id"], "query": q["query"], "sql": "",
                "overall": 0.0, "latency_ms": round(elapsed, 1), "error": str(e),
            })
            failed += 1
            if verbose:
                print(f"{q['id']:<15} {'ERROR':<8} {'0.0':<8} {str(e)[:50]}")

    total_elapsed = (time.perf_counter() - total_start) * 1000

    scores = [r.get("overall", 0) for r in results]
    avg_score = sum(scores) / max(len(scores), 1)

    summary = {
        "total_queries": len(BENCHMARK_SUITE),
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / max(len(BENCHMARK_SUITE), 1) * 100, 1),
        "average_score": round(avg_score, 4),
        "total_duration_ms": round(total_elapsed, 1),
        "avg_latency_ms": round(total_elapsed / max(len(BENCHMARK_SUITE), 1), 1),
        "by_complexity": {},
    }

    by_complexity: dict[str, list[float]] = {}
    for q, r in zip(BENCHMARK_SUITE, results):
        comp = q.get("complexity", "unknown")
        if comp not in by_complexity:
            by_complexity[comp] = []
        by_complexity[comp].append(r.get("overall", 0))

    for comp, comp_scores in by_complexity.items():
        summary["by_complexity"][comp] = {
            "count": len(comp_scores),
            "avg_score": round(sum(comp_scores) / max(len(comp_scores), 1), 4),
        }

    if verbose:
        print("-" * 80)
        print(f"\nSummary:")
        print(f"  Total: {summary['total_queries']}")
        print(f"  Passed: {summary['passed']} ({summary['pass_rate']}%)")
        print(f"  Failed: {summary['failed']}")
        print(f"  Average Score: {summary['average_score']}")
        print(f"  Total Duration: {summary['total_duration_ms']}ms")
        print(f"  Avg Latency: {summary['avg_latency_ms']}ms")
        print(f"\n  By Complexity:")
        for comp, data in summary["by_complexity"].items():
            print(f"    {comp}: {data['avg_score']} ({data['count']} queries)")

    return {"summary": summary, "results": results}
