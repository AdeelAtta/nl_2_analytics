from __future__ import annotations

import uuid
from typing import Any

from ke.models.planning import (
    AggregationSpec,
    ColumnRef,
    CostEstimate,
    GroupingSpec,
    JoinEdge,
    PlanOperation,
    PlanStep,
    QueryIntent,
    QueryPlan,
    QueryType,
    ValidationError,
    ValidationResult,
    ValidationSeverity,
)


class QueryPlanner:
    def __init__(self, intent_agent: Any | None = None) -> None:
        self._intent_agent = intent_agent

    async def create_plan(
        self,
        query: str,
        intent: QueryIntent,
        context: dict[str, Any] | None = None,
    ) -> QueryPlan:
        plan_id = str(uuid.uuid4())
        steps: list[PlanStep] = []
        step_num = 0

        for table in intent.tables:
            step_num += 1
            step_id = f"step_{step_num}"
            plan_step = PlanStep(
                id=step_id,
                step_number=step_num,
                operation=PlanOperation.SCAN,
                tables=[table],
                estimated_rows=10000,
            )
            steps.append(plan_step)

        if intent.filters:
            prev_id = steps[-1].id if steps else ""
            step_num += 1
            step_id = f"step_{step_num}"
            filter_step = PlanStep(
                id=step_id,
                step_number=step_num,
                operation=PlanOperation.FILTER,
                filters=intent.filters,
                dependencies=[prev_id] if prev_id else [],
                estimated_rows=1000,
            )
            steps.append(filter_step)

        if intent.join_edges and len(intent.tables) >= 2:
            prev_id = steps[-1].id if steps else ""
            step_num += 1
            step_id = f"step_{step_num}"
            join_edges = [
                JoinEdge(**e) if isinstance(e, dict) else e
                for e in intent.join_edges
            ]
            join_step = PlanStep(
                id=step_id,
                step_number=step_num,
                operation=PlanOperation.JOIN,
                tables=intent.tables,
                joins=join_edges,
                dependencies=[prev_id] if prev_id else [],
                estimated_rows=5000,
            )
            steps.append(join_step)

        if intent.aggregations:
            prev_id = steps[-1].id if steps else ""
            step_num += 1
            step_id = f"step_{step_num}"
            group_cols = [ColumnRef(table=intent.tables[0].name, column="")] if intent.tables else []
            agg_step = PlanStep(
                id=step_id,
                step_number=step_num,
                operation=PlanOperation.AGGREGATE,
                grouping=GroupingSpec(columns=group_cols),
                aggregations=[
                    AggregationSpec(
                        function=a.get("function", ""),
                        column=ColumnRef(
                            table=intent.tables[0].name if intent.tables else "",
                            column=a.get("column", ""),
                        ),
                        alias=f"{a.get('function', 'agg').lower()}_{a.get('column', 'col')}",
                    )
                    for a in intent.aggregations
                ],
                dependencies=[prev_id] if prev_id else [],
                estimated_rows=100,
            )
            steps.append(agg_step)

        validation = self._validate_plan(intent, steps, context)
        cost = self._estimate_cost(steps)

        return QueryPlan(
            id=plan_id,
            intent=intent,
            steps=steps,
            validation=validation,
            cost_estimate=cost,
            metadata={
                "query": query,
                "table_count": len(intent.tables),
                "join_count": len(intent.join_edges),
                "step_count": len(steps),
            },
        )

    def _validate_plan(
        self,
        intent: QueryIntent,
        steps: list[PlanStep],
        context: dict[str, Any] | None,
    ) -> ValidationResult:
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []

        for table in intent.tables:
            if table.id == "" and table.name:
                warnings.append(ValidationError(
                    code="PLAN-001",
                    severity=ValidationSeverity.WARNING,
                    message=f"Table '{table.name}' not found in schema store",
                    suggestion="Verify the table name and try again",
                ))

        for edge in intent.join_edges:
            src_col = edge.get("source_column", "") if isinstance(edge, dict) else getattr(edge, "source_column", "")
            tgt_col = edge.get("target_column", "") if isinstance(edge, dict) else getattr(edge, "target_column", "")
            src_tbl = edge.get("source_table", "") if isinstance(edge, dict) else getattr(edge, "source_table", "")
            tgt_tbl = edge.get("target_table", "") if isinstance(edge, dict) else getattr(edge, "target_table", "")
            if not src_col or not tgt_col:
                warnings.append(ValidationError(
                    code="PLAN-005",
                    severity=ValidationSeverity.WARNING,
                    message=f"Join between '{src_tbl}' and '{tgt_tbl}' has no columns",
                    suggestion="Specify the join columns",
                ))

        for agg in intent.aggregations:
            if not agg.get("column"):
                errors.append(ValidationError(
                    code="PLAN-008",
                    severity=ValidationSeverity.FATAL,
                    message=f"Aggregate function '{agg.get('function', '')}' requires a column",
                ))

        for step in steps:
            if step.estimated_rows > 1_000_000:
                warnings.append(ValidationError(
                    step_id=step.id,
                    code="PLAN-014",
                    severity=ValidationSeverity.WARNING,
                    message=f"Step {step.step_number} estimated to return {step.estimated_rows:,} rows",
                    suggestion="Add filters or aggregation to reduce result size",
                ))

        if intent.query_type == QueryType.UNKNOWN:
            errors.append(ValidationError(
                code="PLAN-000",
                severity=ValidationSeverity.FATAL,
                message="Could not determine query intent",
            ))

        if intent.query_type == QueryType.DDL:
            errors.append(ValidationError(
                code="PLAN-015",
                severity=ValidationSeverity.FATAL,
                message="DDL operations are not supported",
            ))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _estimate_cost(self, steps: list[PlanStep]) -> CostEstimate:
        total_rows = sum(s.estimated_rows for s in steps)
        cost_factors = {
            PlanOperation.SCAN: 1.0,
            PlanOperation.FILTER: 0.5,
            PlanOperation.JOIN: 2.0,
            PlanOperation.AGGREGATE: 1.5,
            PlanOperation.WINDOW: 2.0,
            PlanOperation.SORT: 0.1,
            PlanOperation.LIMIT: 0.1,
            PlanOperation.PROJECT: 0.3,
            PlanOperation.DISTINCT: 1.5,
            PlanOperation.SUBQUERY_EXEC: 2.0,
            PlanOperation.UNION: 1.5,
            PlanOperation.CTE: 1.0,
        }
        total_cost = sum(
            s.estimated_rows * cost_factors.get(s.operation, 1.0)
            for s in steps
        )
        estimated_ms = total_cost * 0.01
        if total_cost > 1000:
            estimated_ms = total_cost * 0.05
        return CostEstimate(
            estimated_rows=total_rows,
            estimated_cost=round(total_cost, 2),
            estimated_duration_ms=round(estimated_ms, 2),
        )

    async def plan(
        self,
        query: str,
        context: dict[str, Any] | None = None,
        intent: QueryIntent | None = None,
    ) -> QueryPlan:
        if intent is None and self._intent_agent is not None:
            intent = self._intent_agent.classify(query, context)
        elif intent is None:
            raise ValueError("Either intent or intent_agent must be provided")

        return await self.create_plan(query, intent, context)
