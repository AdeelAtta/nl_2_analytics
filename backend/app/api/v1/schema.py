from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.auth.dependencies import get_current_user
from ke.services.schema_registry import get_schema, list_databases as list_registry_dbs

router = APIRouter(prefix="/api/v1/schema", tags=["schema"])


def _auth(current_user: dict[str, str]) -> str:
    if current_user.get("sub") == "anonymous":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return current_user.get("tenant_id", "demo")


def _empty(page=1, ps=50):
    return {"success": True, "data": [], "meta": {"page": page, "page_size": ps, "total": 0}}


def _registry_tables(tenant_id: str, page: int, page_size: int, db_name: str = "") -> dict[str, Any] | None:
    schema = get_schema(tenant_id, db_name)
    if not schema or not schema.get("tables"):
        return None
    tables = schema["tables"]
    start = (page - 1) * page_size
    end = start + page_size
    page_data = tables[start:end]
    return {
        "success": True,
        "data": [
            {"id": f"reg-{t['name']}", "name": t["name"], "description": t.get("description", ""), "schema_name": ""}
            for t in page_data
        ],
        "meta": {"page": page, "page_size": page_size, "total": len(tables)},
    }


@router.get("/tables")
async def list_tables(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    database: str = Query(""),
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    tenant_id = _auth(current_user)

    reg = _registry_tables(tenant_id, page, page_size, database)
    if reg:
        return reg

    return _empty(page, page_size)


@router.get("/tables/{table_id}")
async def get_table(
    table_id: str,
    database: str = Query(""),
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    tenant_id = _auth(current_user)

    schema = get_schema(tenant_id, database)
    if schema and schema.get("tables"):
        for t in schema["tables"]:
            if t["name"] == table_id or f"reg-{t['name']}" == table_id:
                rows = t.get("sample_rows", [])
                return {
                    "success": True,
                    "data": {
                        "id": table_id,
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "sample_rows": rows,
                        "columns": [
                            {
                                "id": f"col-{c['name']}",
                                "name": c["name"],
                                "data_type": c["data_type"],
                                "is_nullable": c.get("is_nullable", True),
                                "is_primary_key": c.get("is_primary_key", False),
                                "description": c.get("description", ""),
                            }
                            for c in t.get("columns", [])
                        ],
                    },
                }

    raise HTTPException(status_code=404, detail="Table not found")


@router.get("/databases")
async def list_databases(
    request: Request,
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    tenant_id = _auth(current_user)
    dbs = list_registry_dbs(tenant_id)
    return {"success": True, "data": dbs}


@router.get("/search")
async def search_schema(
    request: Request,
    q: str = Query("", min_length=1),
    current_user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    tenant_id = _auth(current_user)
    ql = q.lower()

    dbs = list_registry_dbs(tenant_id)
    results: list[dict[str, str]] = []
    for db in dbs:
        schema = get_schema(tenant_id, db.get("database", db.get("name", "")))
        if schema and schema.get("tables"):
            for t in schema["tables"]:
                if ql in t["name"].lower() or (t.get("description") and ql in t["description"].lower()):
                    results.append({"id": f"reg-{t['name']}", "name": t["name"], "type": "table", "description": t.get("description", "")})
    return {"success": True, "data": results[:20]}
