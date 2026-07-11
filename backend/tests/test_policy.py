from __future__ import annotations

from typing import Any

import pytest

from ke.models.policy import PolicyChainResult
from ke.services.policy.base import PolicyLayerBase
from ke.services.policy.chain import PolicyChain
from ke.services.policy.layers import (
    L1IntentClassificationLayer,
    L2SQLSanitizationLayer,
    L3RBACSchemaScopingLayer,
    L4CostCeilingLayer,
    L5SQLValidationLayer,
    L6ReadOnlyEnforcementLayer,
    L7AuditLoggingLayer,
    L8DataClassificationLayer,
    L9AdvancedValidationLayer,
    L10AnomalyDetectionLayer,
)


@pytest.fixture
def policy_chain() -> PolicyChain:
    return PolicyChain()


@pytest.fixture
def sample_context() -> dict[str, Any]:
    return {
        "columns": [
            {"name": "id", "table_name": "users", "data_type": "integer"},
            {"name": "email", "table_name": "users", "data_type": "varchar"},
            {"name": "name", "table_name": "users", "data_type": "varchar"},
            {"name": "phone", "table_name": "users", "data_type": "varchar"},
        ],
        "recent_queries": ["SELECT 1", "SELECT * FROM users", "SELECT name FROM users WHERE id = 1"],
    }


class TestL1IntentClassification:
    @pytest.mark.asyncio
    async def test_allows_select(self) -> None:
        layer = L1IntentClassificationLayer()
        result = await layer.run("SELECT * FROM users")
        assert result.passed

    @pytest.mark.asyncio
    async def test_blocks_insert(self) -> None:
        layer = L1IntentClassificationLayer()
        result = await layer.run("INSERT INTO users VALUES (1)")
        assert not result.passed

    @pytest.mark.asyncio
    async def test_blocks_ddl(self) -> None:
        layer = L1IntentClassificationLayer()
        result = await layer.run("DROP TABLE users")
        assert not result.passed

    @pytest.mark.asyncio
    async def test_empty_sql_blocked(self) -> None:
        layer = L1IntentClassificationLayer()
        result = await layer.run("")
        assert not result.passed


class TestL2SQLSanitization:
    @pytest.mark.asyncio
    async def test_passes_clean_sql(self) -> None:
        layer = L2SQLSanitizationLayer()
        result = await layer.run("SELECT * FROM users WHERE id = 1")
        assert result.passed

    @pytest.mark.asyncio
    async def test_removes_null_bytes(self) -> None:
        layer = L2SQLSanitizationLayer()
        result = await layer.run("SELECT * FROM users WHERE id = 1\x00DROP TABLE users")
        assert result.passed
        assert "\x00" not in result.metadata.get("sanitized_sql", "")

    @pytest.mark.asyncio
    async def test_strips_sql_comments(self) -> None:
        layer = L2SQLSanitizationLayer()
        result = await layer.run("SELECT * FROM users; -- DROP TABLE users")
        assert result.passed

    @pytest.mark.asyncio
    async def test_detects_union_select(self) -> None:
        layer = L2SQLSanitizationLayer()
        result = await layer.run("SELECT * FROM users UNION SELECT * FROM admins")
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_detects_or_1_equals_1(self) -> None:
        layer = L2SQLSanitizationLayer()
        result = await layer.run("SELECT * FROM users WHERE id = 1 OR 1=1")
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_detects_information_schema(self) -> None:
        layer = L2SQLSanitizationLayer()
        result = await layer.run("SELECT * FROM INFORMATION_SCHEMA.TABLES")
        assert not result.passed
        assert result.blocked


class TestL3RBAC:
    @pytest.mark.asyncio
    async def test_passes_with_authorized_tables(self) -> None:
        layer = L3RBACSchemaScopingLayer()
        result = await layer.run("SELECT * FROM users", {"authorized_tables": ["users", "orders"]})
        assert result.passed

    @pytest.mark.asyncio
    async def test_blocks_unauthorized_table(self) -> None:
        layer = L3RBACSchemaScopingLayer()
        result = await layer.run("SELECT * FROM admins", {"authorized_tables": ["users", "orders"]})
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_skips_without_context(self) -> None:
        layer = L3RBACSchemaScopingLayer()
        result = await layer.run("SELECT * FROM admins")
        assert result.passed


class TestL4CostCeiling:
    @pytest.mark.asyncio
    async def test_passes_within_limit(self) -> None:
        layer = L4CostCeilingLayer()
        result = await layer.run("SELECT * FROM users", {"estimated_rows": 1000})
        assert result.passed

    @pytest.mark.asyncio
    async def test_blocks_excessive_rows(self) -> None:
        layer = L4CostCeilingLayer()
        result = await layer.run("SELECT * FROM users", {"estimated_rows": 20_000_000})
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_skips_without_context(self) -> None:
        layer = L4CostCeilingLayer()
        result = await layer.run("SELECT * FROM users")
        assert result.passed


class TestL5SQLValidation:
    @pytest.mark.asyncio
    async def test_passes_valid_sql(self) -> None:
        layer = L5SQLValidationLayer()
        result = await layer.run("SELECT * FROM users WHERE id = 1")
        assert result.passed

    @pytest.mark.asyncio
    async def test_fails_invalid_sql(self) -> None:
        layer = L5SQLValidationLayer()
        result = await layer.run("SELECT * FROM")
        assert not result.passed

    @pytest.mark.asyncio
    async def test_fails_gibberish(self) -> None:
        layer = L5SQLValidationLayer()
        result = await layer.run("NOT SQL AT ALL")
        assert not result.passed


class TestL6ReadOnly:
    @pytest.mark.asyncio
    async def test_passes_select(self) -> None:
        layer = L6ReadOnlyEnforcementLayer()
        result = await layer.run("SELECT * FROM users")
        assert result.passed

    @pytest.mark.asyncio
    async def test_blocks_insert(self) -> None:
        layer = L6ReadOnlyEnforcementLayer()
        result = await layer.run("INSERT INTO users (id) VALUES (1)")
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_blocks_update(self) -> None:
        layer = L6ReadOnlyEnforcementLayer()
        result = await layer.run("UPDATE users SET name = 'test' WHERE id = 1")
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_blocks_delete(self) -> None:
        layer = L6ReadOnlyEnforcementLayer()
        result = await layer.run("DELETE FROM users WHERE id = 1")
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_blocks_create_table(self) -> None:
        layer = L6ReadOnlyEnforcementLayer()
        result = await layer.run("CREATE TABLE test (id INT)")
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_blocks_alter_table(self) -> None:
        layer = L6ReadOnlyEnforcementLayer()
        result = await layer.run("ALTER TABLE users ADD COLUMN age INT")
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_blocks_drop_table(self) -> None:
        layer = L6ReadOnlyEnforcementLayer()
        result = await layer.run("DROP TABLE users")
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_blocks_grant(self) -> None:
        layer = L6ReadOnlyEnforcementLayer()
        result = await layer.run("GRANT SELECT ON users TO test_user")
        assert not result.passed
        assert result.blocked


class TestL7AuditLogging:
    @pytest.mark.asyncio
    async def test_logs_query(self) -> None:
        layer = L7AuditLoggingLayer()
        result = await layer.run("SELECT * FROM users", {"tenant_id": "t1", "user_id": "u1"})
        assert result.passed
        assert "log_entry" in result.metadata

    @pytest.mark.asyncio
    async def test_logs_without_context(self) -> None:
        layer = L7AuditLoggingLayer()
        result = await layer.run("SELECT * FROM users")
        assert result.passed


class TestL8DataClassification:
    @pytest.mark.asyncio
    async def test_detects_email_column(self) -> None:
        layer = L8DataClassificationLayer()
        result = await layer.run("SELECT email FROM users", {
            "columns": [{"name": "email", "table_name": "users", "data_type": "varchar"}],
        })
        assert result.passed
        assert result.metadata.get("pii_count", 0) == 1

    @pytest.mark.asyncio
    async def test_detects_phone_column(self) -> None:
        layer = L8DataClassificationLayer()
        result = await layer.run("SELECT phone FROM users", {
            "columns": [{"name": "phone", "table_name": "users", "data_type": "varchar"}],
        })
        assert result.passed
        assert result.metadata.get("pii_count", 0) == 1

    @pytest.mark.asyncio
    async def test_skips_without_context(self) -> None:
        layer = L8DataClassificationLayer()
        result = await layer.run("SELECT email FROM users")
        assert result.passed

    @pytest.mark.asyncio
    async def test_skips_non_pii_column(self) -> None:
        layer = L8DataClassificationLayer()
        result = await layer.run("SELECT id FROM users", {
            "columns": [{"name": "id", "table_name": "users", "data_type": "integer"}],
        })
        assert result.passed
        assert result.metadata.get("pii_count", 0) == 0


class TestL9AdvancedValidation:
    @pytest.mark.asyncio
    async def test_passes_normal_sql(self) -> None:
        layer = L9AdvancedValidationLayer()
        result = await layer.run("SELECT * FROM users")
        assert result.passed

    @pytest.mark.asyncio
    async def test_blocks_exec(self) -> None:
        layer = L9AdvancedValidationLayer()
        result = await layer.run("EXEC xp_cmdshell 'dir'")
        assert not result.passed
        assert result.blocked

    @pytest.mark.asyncio
    async def test_blocks_sp_executesql(self) -> None:
        layer = L9AdvancedValidationLayer()
        result = await layer.run("EXEC sp_executesql N'SELECT * FROM users'")
        assert not result.passed
        assert result.blocked


class TestL10AnomalyDetection:
    @pytest.mark.asyncio
    async def test_passes_normal_query(self) -> None:
        layer = L10AnomalyDetectionLayer()
        result = await layer.run("SELECT * FROM users", {
            "recent_queries": ["SELECT 1", "SELECT * FROM users", "SELECT name FROM users WHERE id = 1"],
        })
        assert result.passed

    @pytest.mark.asyncio
    async def test_skips_without_context(self) -> None:
        layer = L10AnomalyDetectionLayer()
        result = await layer.run("SELECT * FROM users")
        assert result.passed

    @pytest.mark.asyncio
    async def test_skips_without_baseline(self) -> None:
        layer = L10AnomalyDetectionLayer()
        result = await layer.run("SELECT * FROM users", {"recent_queries": []})
        assert result.passed


class TestPolicyChain:
    @pytest.mark.asyncio
    async def test_passes_clean_select(self, policy_chain: PolicyChain, sample_context: dict[str, Any]) -> None:
        result = await policy_chain.enforce("SELECT * FROM users WHERE id = 1", sample_context)
        assert result.passed
        assert result.stopped_at is None
        assert len(result.layers) == 10

    @pytest.mark.asyncio
    async def test_blocks_insert(self, policy_chain: PolicyChain) -> None:
        result = await policy_chain.enforce("INSERT INTO users (id) VALUES (1)")
        assert not result.passed
        assert result.stopped_at == "intent_classification"

    @pytest.mark.asyncio
    async def test_blocks_drop(self, policy_chain: PolicyChain) -> None:
        result = await policy_chain.enforce("DROP TABLE users")
        assert not result.passed
        assert result.stopped_at == "intent_classification"

    @pytest.mark.asyncio
    async def test_blocks_sql_injection(self, policy_chain: PolicyChain) -> None:
        result = await policy_chain.enforce("SELECT * FROM users WHERE id = 1 OR 1=1")
        assert not result.passed
        assert result.stopped_at == "sql_sanitization"

    @pytest.mark.asyncio
    async def test_blocks_dml_write(self, policy_chain: PolicyChain) -> None:
        result = await policy_chain.enforce("DELETE FROM users WHERE id = 1")
        assert not result.passed
        assert result.stopped_at == "intent_classification"

    @pytest.mark.asyncio
    async def test_sanitizes_sql(self, policy_chain: PolicyChain) -> None:
        result = await policy_chain.enforce("SELECT * FROM users; -- comment")
        assert result.sanitized_sql == "SELECT * FROM users;"
        assert result.passed

    @pytest.mark.asyncio
    async def test_all_layers_executed_on_success(self, policy_chain: PolicyChain, sample_context: dict[str, Any]) -> None:
        result = await policy_chain.enforce("SELECT * FROM users WHERE id = 1", sample_context)
        assert len(result.layers) == 10
        assert all(l.passed for l in result.layers)

    @pytest.mark.asyncio
    async def test_result_has_layer_details(self, policy_chain: PolicyChain) -> None:
        result = await policy_chain.enforce("SELECT 1")
        for layer in result.layers:
            assert layer.layer_name
            assert layer.layer_number >= 1
            assert layer.duration_ms >= 0


class TestCustomLayer:
    @pytest.mark.asyncio
    async def test_custom_layer_in_chain(self) -> None:
        class CustomAllowLayer(PolicyLayerBase):
            layer_number = 99
            layer_name = "custom_allow"

            async def check(self, sql: str, context: dict[str, Any] | None = None):
                from ke.models.policy import PolicyLayerResult
                return PolicyLayerResult(passed=True, reason="Custom allow")

        chain = PolicyChain(layers=[CustomAllowLayer()])
        result = await chain.enforce("SELECT 1")
        assert result.passed
        assert len(result.layers) == 1

    @pytest.mark.asyncio
    async def test_custom_blocking_layer(self) -> None:
        class CustomBlockLayer(PolicyLayerBase):
            layer_number = 99
            layer_name = "custom_block"

            async def check(self, sql: str, context: dict[str, Any] | None = None):
                from ke.models.policy import PolicyLayerResult
                return PolicyLayerResult(passed=False, blocked=True, reason="Always block")

        chain = PolicyChain(layers=[CustomBlockLayer()])
        result = await chain.enforce("SELECT 1")
        assert not result.passed
        assert result.stopped_at == "custom_block"
