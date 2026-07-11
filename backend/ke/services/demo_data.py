from __future__ import annotations

from typing import Any

DEMO_TABLES: list[dict[str, Any]] = [
    {"id": "demo-t1", "name": "users", "schema_name": "public", "description": "User accounts and profiles"},
    {"id": "demo-t2", "name": "orders", "schema_name": "public", "description": "Customer orders and transactions"},
    {"id": "demo-t3", "name": "products", "schema_name": "public", "description": "Product catalog and inventory"},
    {"id": "demo-t4", "name": "customers", "schema_name": "public", "description": "Customer information and demographics"},
    {"id": "demo-t5", "name": "revenue", "schema_name": "public", "description": "Revenue and financial data by quarter"},
    {"id": "demo-t6", "name": "employees", "schema_name": "public", "description": "Employee records and departments"},
    {"id": "demo-t7", "name": "categories", "schema_name": "public", "description": "Product categories"},
    {"id": "demo-t8", "name": "inventory", "schema_name": "public", "description": "Stock levels and warehouse data"},
    {"id": "demo-t9", "name": "departments", "schema_name": "public", "description": "Company departments"},
    {"id": "demo-t10", "name": "payments", "schema_name": "public", "description": "Payment transactions"},
]

DEMO_COLUMNS: list[dict[str, Any]] = [
    {"id": "dc1", "table_id": "demo-t1", "table_name": "users", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Unique user identifier"},
    {"id": "dc2", "table_id": "demo-t1", "table_name": "users", "name": "name", "data_type": "VARCHAR(255)", "is_primary_key": False, "is_nullable": False, "description": "User full name"},
    {"id": "dc3", "table_id": "demo-t1", "table_name": "users", "name": "email", "data_type": "VARCHAR(255)", "is_primary_key": False, "is_nullable": False, "description": "User email address"},
    {"id": "dc4", "table_id": "demo-t1", "table_name": "users", "name": "status", "data_type": "VARCHAR(50)", "is_primary_key": False, "is_nullable": False, "description": "Account status (active/inactive/suspended)"},
    {"id": "dc5", "table_id": "demo-t1", "table_name": "users", "name": "created_at", "data_type": "TIMESTAMP", "is_primary_key": False, "is_nullable": False, "description": "Account creation timestamp"},
    {"id": "dc6", "table_id": "demo-t2", "table_name": "orders", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Order ID"},
    {"id": "dc7", "table_id": "demo-t2", "table_name": "orders", "name": "customer_id", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "FK to customers"},
    {"id": "dc8", "table_id": "demo-t2", "table_name": "orders", "name": "product_id", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "FK to products"},
    {"id": "dc9", "table_id": "demo-t2", "table_name": "orders", "name": "quantity", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "Quantity ordered"},
    {"id": "dc10", "table_id": "demo-t2", "table_name": "orders", "name": "total_amount", "data_type": "DECIMAL(10,2)", "is_primary_key": False, "is_nullable": False, "description": "Order total"},
    {"id": "dc11", "table_id": "demo-t2", "table_name": "orders", "name": "status", "data_type": "VARCHAR(50)", "is_primary_key": False, "is_nullable": False, "description": "Order status"},
    {"id": "dc12", "table_id": "demo-t2", "table_name": "orders", "name": "order_date", "data_type": "DATE", "is_primary_key": False, "is_nullable": False, "description": "Order date"},
    {"id": "dc13", "table_id": "demo-t2", "table_name": "orders", "name": "created_at", "data_type": "TIMESTAMP", "is_primary_key": False, "is_nullable": False, "description": "Order creation timestamp"},
    {"id": "dc14", "table_id": "demo-t3", "table_name": "products", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Product ID"},
    {"id": "dc15", "table_id": "demo-t3", "table_name": "products", "name": "name", "data_type": "VARCHAR(255)", "is_primary_key": False, "is_nullable": False, "description": "Product name"},
    {"id": "dc16", "table_id": "demo-t3", "table_name": "products", "name": "category_id", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "FK to categories"},
    {"id": "dc17", "table_id": "demo-t3", "table_name": "products", "name": "price", "data_type": "DECIMAL(10,2)", "is_primary_key": False, "is_nullable": False, "description": "Product price"},
    {"id": "dc18", "table_id": "demo-t3", "table_name": "products", "name": "stock_quantity", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "Current stock level"},
    {"id": "dc19", "table_id": "demo-t4", "table_name": "customers", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Customer ID"},
    {"id": "dc20", "table_id": "demo-t4", "table_name": "customers", "name": "name", "data_type": "VARCHAR(255)", "is_primary_key": False, "is_nullable": False, "description": "Customer name"},
    {"id": "dc21", "table_id": "demo-t4", "table_name": "customers", "name": "email", "data_type": "VARCHAR(255)", "is_primary_key": False, "is_nullable": False, "description": "Customer email"},
    {"id": "dc22", "table_id": "demo-t4", "table_name": "customers", "name": "city", "data_type": "VARCHAR(100)", "is_primary_key": False, "is_nullable": False, "description": "Customer city"},
    {"id": "dc23", "table_id": "demo-t4", "table_name": "customers", "name": "state", "data_type": "VARCHAR(50)", "is_primary_key": False, "is_nullable": False, "description": "Customer state"},
    {"id": "dc24", "table_id": "demo-t4", "table_name": "customers", "name": "signup_date", "data_type": "DATE", "is_primary_key": False, "is_nullable": False, "description": "Customer signup date"},
    {"id": "dc25", "table_id": "demo-t5", "table_name": "revenue", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Revenue record ID"},
    {"id": "dc26", "table_id": "demo-t5", "table_name": "revenue", "name": "quarter", "data_type": "VARCHAR(10)", "is_primary_key": False, "is_nullable": False, "description": "Fiscal quarter"},
    {"id": "dc27", "table_id": "demo-t5", "table_name": "revenue", "name": "year", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "Fiscal year"},
    {"id": "dc28", "table_id": "demo-t5", "table_name": "revenue", "name": "amount", "data_type": "DECIMAL(15,2)", "is_primary_key": False, "is_nullable": False, "description": "Revenue amount"},
    {"id": "dc29", "table_id": "demo-t6", "table_name": "employees", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Employee ID"},
    {"id": "dc30", "table_id": "demo-t6", "table_name": "employees", "name": "name", "data_type": "VARCHAR(255)", "is_primary_key": False, "is_nullable": False, "description": "Employee name"},
    {"id": "dc31", "table_id": "demo-t6", "table_name": "employees", "name": "department_id", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "FK to departments"},
    {"id": "dc32", "table_id": "demo-t6", "table_name": "employees", "name": "salary", "data_type": "DECIMAL(10,2)", "is_primary_key": False, "is_nullable": False, "description": "Employee salary"},
    {"id": "dc33", "table_id": "demo-t7", "table_name": "categories", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Category ID"},
    {"id": "dc34", "table_id": "demo-t7", "table_name": "categories", "name": "name", "data_type": "VARCHAR(255)", "is_primary_key": False, "is_nullable": False, "description": "Category name"},
    {"id": "dc35", "table_id": "demo-t8", "table_name": "inventory", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Inventory record ID"},
    {"id": "dc36", "table_id": "demo-t8", "table_name": "inventory", "name": "product_id", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "FK to products"},
    {"id": "dc37", "table_id": "demo-t8", "table_name": "inventory", "name": "warehouse", "data_type": "VARCHAR(100)", "is_primary_key": False, "is_nullable": False, "description": "Warehouse location"},
    {"id": "dc38", "table_id": "demo-t8", "table_name": "inventory", "name": "quantity", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "Available quantity"},
    {"id": "dc39", "table_id": "demo-t9", "table_name": "departments", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Department ID"},
    {"id": "dc40", "table_id": "demo-t9", "table_name": "departments", "name": "name", "data_type": "VARCHAR(255)", "is_primary_key": False, "is_nullable": False, "description": "Department name"},
    {"id": "dc41", "table_id": "demo-t9", "table_name": "departments", "name": "budget", "data_type": "DECIMAL(15,2)", "is_primary_key": False, "is_nullable": False, "description": "Department budget"},
    {"id": "dc42", "table_id": "demo-t10", "table_name": "payments", "name": "id", "data_type": "INTEGER", "is_primary_key": True, "is_nullable": False, "description": "Payment ID"},
    {"id": "dc43", "table_id": "demo-t10", "table_name": "payments", "name": "order_id", "data_type": "INTEGER", "is_primary_key": False, "is_nullable": False, "description": "FK to orders"},
    {"id": "dc44", "table_id": "demo-t10", "table_name": "payments", "name": "amount", "data_type": "DECIMAL(10,2)", "is_primary_key": False, "is_nullable": False, "description": "Payment amount"},
    {"id": "dc45", "table_id": "demo-t10", "table_name": "payments", "name": "method", "data_type": "VARCHAR(50)", "is_primary_key": False, "is_nullable": False, "description": "Payment method"},
    {"id": "dc46", "table_id": "demo-t10", "table_name": "payments", "name": "payment_date", "data_type": "DATE", "is_primary_key": False, "is_nullable": False, "description": "Payment date"},
]

DEMO_RELATIONSHIPS: list[dict[str, Any]] = [
    {"source_table": "orders", "source_column": "customer_id", "target_table": "customers", "target_column": "id", "relationship_type": "foreign_key"},
    {"source_table": "orders", "source_column": "product_id", "target_table": "products", "target_column": "id", "relationship_type": "foreign_key"},
    {"source_table": "products", "source_column": "category_id", "target_table": "categories", "target_column": "id", "relationship_type": "foreign_key"},
    {"source_table": "employees", "source_column": "department_id", "target_table": "departments", "target_column": "id", "relationship_type": "foreign_key"},
    {"source_table": "inventory", "source_column": "product_id", "target_table": "products", "target_column": "id", "relationship_type": "foreign_key"},
    {"source_table": "payments", "source_column": "order_id", "target_table": "orders", "target_column": "id", "relationship_type": "foreign_key"},
]


def get_demo_context() -> dict[str, Any]:
    return {
        "tables": DEMO_TABLES,
        "columns": DEMO_COLUMNS,
        "relationships": DEMO_RELATIONSHIPS,
        "ddl_context": _build_demo_ddl(),
    }


def _build_demo_ddl() -> str:
    lines: list[str] = []
    for tbl in DEMO_TABLES:
        tbl_name = tbl["name"]
        cols = [c for c in DEMO_COLUMNS if c.get("table_name") == tbl_name]
        lines.append(f"CREATE TABLE {tbl_name} (")
        for col in cols:
            parts = [f"  {col['name']} {col['data_type']}"]
            if col.get("is_primary_key"):
                parts.append("PRIMARY KEY")
            if not col.get("is_nullable", True):
                parts.append("NOT NULL")
            lines.append(" ".join(parts))
        lines.append(");")
        for rel in DEMO_RELATIONSHIPS:
            if rel["source_table"] == tbl_name:
                lines.append(f"-- {rel['source_table']}.{rel['source_column']} -> {rel['target_table']}.{rel['target_column']}")
    return "\n".join(lines)
