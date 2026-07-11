from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ke.api.schemas import success_response
from ke.services.executor import QueryExecutor


class ExecuteRequest(BaseModel):
    sql: str = Field(..., min_length=1, description="SQL query to execute")
    params: dict[str, Any] | None = None
    timeout: float = Field(default=30.0, ge=1.0, le=300.0)
    page: int = Field(default=1, ge=1, le=10000)
    page_size: int = Field(default=1000, ge=1, le=10000)
    dry_run: bool = False

router = APIRouter(tags=["executor"])

_executor = QueryExecutor()


def get_executor() -> QueryExecutor:
    return _executor


@router.post("/v1/ke/execute")
async def execute_sql(
    body: ExecuteRequest,
    executor: QueryExecutor = Depends(get_executor),
) -> dict[str, Any]:
    result = await executor.execute(
        body.sql, body.params, body.timeout, body.page, body.page_size, body.dry_run
    )
    return success_response(result.model_dump())
