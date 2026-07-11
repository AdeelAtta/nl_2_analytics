from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from schema_intelligence.connectors.base import ConnectorConfig, ConnectorRegistry
from schema_intelligence.sync.orchestrator import SyncOrchestrator

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])

DB_TYPES = {
    "postgresql": "postgresql",
    "mysql": "mysql",
    "snowflake": "snowflake",
    "bigquery": "bigquery",
    "duckdb": "duckdb",
}


class SyncConnectionRequest(BaseModel):
    db_type: str = "postgresql"
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    username: str = ""
    password: str = ""


@router.post("/test")
async def test_connection(
    body: SyncConnectionRequest,
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    config = ConnectorConfig(
        host=body.host,
        port=body.port,
        database=body.database or body.db_type,
        username=body.username,
        password=body.password,
        timeout_seconds=10,
    )
    try:
        registry = ConnectorRegistry()
        connector_cls = registry.get(body.db_type)
        connector = connector_cls()
        await connector.connect(config)
        await connector.disconnect()
        return {"success": True, "data": {"status": "connected",
                                          "host": body.host, "port": body.port}}
    except Exception as e:
        return {"success": False, "error": f"Connection failed: {str(e)[:200]}"}


@router.post("/extract")
async def sync_and_extract(
    body: SyncConnectionRequest,
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    config = ConnectorConfig(
        host=body.host,
        port=body.port,
        database=body.database or body.db_type,
        username=body.username,
        password=body.password,
        timeout_seconds=30,
    )
    tenant_id = current_user.get("tenant_id", "default")
    try:
        orchestrator = SyncOrchestrator()
        result = await orchestrator.sync(config, db_type=body.db_type)
        tables = []
        all_columns: list[dict[str, Any]] = []
        for table in result.added + result.changed:
            cols = []
            for c in table.columns:
                col = {
                    "name": c.name,
                    "data_type": c.data_type,
                    "is_primary_key": c.is_primary_key,
                    "is_nullable": c.is_nullable,
                    "ordinal_position": c.ordinal_position,
                    "table_name": table.name,
                }
                cols.append(col)
                all_columns.append(col)
            tables.append({"name": table.name, "columns": cols})

        from ke.services.schema_registry import store_schema
        store_schema(tenant_id, tables, all_columns)

        return {
            "success": True,
            "data": {
                "tables": tables,
                "added": len(result.added),
                "changed": len(result.changed),
                "removed": len(result.removed),
            },
        }
    except Exception as e:
        return {"success": False, "error": f"Sync failed: {str(e)[:300]}"}
