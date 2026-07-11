"""Add missing indexes on foreign key columns for query performance.

Revision ID: 006
Revises: 005
Create Date: 2026-07-11

"""
# ruff: noqa: E501
from collections.abc import Sequence

from alembic import op

revision: str = "006"
down_revision: str | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_SS = "schema_store"
_GS = "graph_store"
_QS = "query_store"


def upgrade() -> None:
    op.create_index("idx_databases_tenant_id", "databases", ["tenant_id"], schema=_SS)
    op.create_index("idx_schema_infos_database_id", "schema_infos", ["database_id"], schema=_SS)
    op.create_index("idx_tables_schema_id", "tables", ["schema_id"], schema=_SS)
    op.create_index("idx_columns_table_id", "columns", ["table_id"], schema=_SS)
    op.create_index("idx_relationships_tenant_id", "relationships", ["tenant_id"], schema=_SS)
    op.create_index("idx_relationships_source_table_id", "relationships", ["source_table_id"], schema=_SS)
    op.create_index("idx_relationships_target_table_id", "relationships", ["target_table_id"], schema=_SS)
    op.create_index("idx_schema_versions_schema_id", "schema_versions", ["schema_id"], schema=_SS)
    op.create_index("idx_graph_nodes_tenant_id", "graph_nodes", ["tenant_id"], schema=_GS)
    op.create_index("idx_graph_edges_tenant_id", "graph_edges", ["tenant_id"], schema=_GS)
    op.create_index("idx_graph_edges_source_node_id", "graph_edges", ["source_node_id"], schema=_GS)
    op.create_index("idx_graph_edges_target_node_id", "graph_edges", ["target_node_id"], schema=_GS)
    op.create_index("idx_query_feedback_query_id", "query_feedback", ["query_id"], schema=_QS)


def downgrade() -> None:
    op.drop_index("idx_databases_tenant_id", table_name="databases", schema=_SS)
    op.drop_index("idx_schema_infos_database_id", table_name="schema_infos", schema=_SS)
    op.drop_index("idx_tables_schema_id", table_name="tables", schema=_SS)
    op.drop_index("idx_columns_table_id", table_name="columns", schema=_SS)
    op.drop_index("idx_relationships_tenant_id", table_name="relationships", schema=_SS)
    op.drop_index("idx_relationships_source_table_id", table_name="relationships", schema=_SS)
    op.drop_index("idx_relationships_target_table_id", table_name="relationships", schema=_SS)
    op.drop_index("idx_schema_versions_schema_id", table_name="schema_versions", schema=_SS)
    op.drop_index("idx_graph_nodes_tenant_id", table_name="graph_nodes", schema=_GS)
    op.drop_index("idx_graph_edges_tenant_id", table_name="graph_edges", schema=_GS)
    op.drop_index("idx_graph_edges_source_node_id", table_name="graph_edges", schema=_GS)
    op.drop_index("idx_graph_edges_target_node_id", table_name="graph_edges", schema=_GS)
    op.drop_index("idx_query_feedback_query_id", table_name="query_feedback", schema=_QS)
