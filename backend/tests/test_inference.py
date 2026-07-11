from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ke.services.inference import (
    HFInferenceClient,
    InferenceFactory,
    MockClient,
    OpenAIClient,
)


class TestHFInferenceClient:
    def test_parse_chat_response_extracts_sql(self) -> None:
        result = {
            "choices": [{"message": {"content": "```sql\nSELECT * FROM users WHERE id = 1;\n```"}}]
        }
        parsed = HFInferenceClient._parse_chat_response(result)
        assert "SELECT * FROM users" in parsed

    def test_parse_chat_response_empty(self) -> None:
        parsed = HFInferenceClient._parse_chat_response({})
        assert parsed is not None

    def test_parse_chat_response_plain_sql(self) -> None:
        result = {
            "choices": [{"message": {"content": "SELECT id, name FROM users WHERE active = true;"}}]
        }
        parsed = HFInferenceClient._parse_chat_response(result)
        assert "SELECT id, name FROM users" in parsed

    def test_parse_chat_response_simple(self) -> None:
        result = {
            "choices": [{"message": {"content": "SELECT 1"}}]
        }
        parsed = HFInferenceClient._parse_chat_response(result)
        assert parsed == "SELECT 1"

    @pytest.mark.asyncio
    async def test_generate_calls_hf_api(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "SELECT * FROM test"}}]
        }

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.post.return_value = mock_resp
            MockClient.return_value = mock_instance

            client = HFInferenceClient("test-model", cost=0.0)
            result = await client.generate("test prompt")

            assert result == "SELECT * FROM test"

    @pytest.mark.asyncio
    async def test_generate_http_error_raises(self) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("HTTP 503")

        async def mock_post(*args, **kwargs):
            return mock_resp

        with patch("httpx.AsyncClient") as MockClient:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.post.return_value = mock_resp
            MockClient.return_value = mock_instance

            client = HFInferenceClient("test-model", cost=0.0)
            with pytest.raises(Exception, match="HTTP 503"):
                await client.generate("test prompt")

    def test_model_name_property(self) -> None:
        client = HFInferenceClient("defog/sqlcoder-7b-2")
        assert client.model_name == "defog/sqlcoder-7b-2"

    def test_cost_property(self) -> None:
        client = HFInferenceClient("test-model", cost=0.005)
        assert client.cost_per_query == 0.005


class TestOpenAIClient:
    @pytest.mark.asyncio
    async def test_generate_returns_sql(self) -> None:
        mock_choice = MagicMock()
        mock_choice.message.content = "SELECT * FROM users"
        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]

        with (
            patch("openai.AsyncOpenAI") as MockOA,
            patch("ke.services.inference.get_settings") as mock_settings,
        ):
            mock_settings.return_value.openai_api_key = "sk-test"
            mock_settings.return_value.openai_org_id = ""
            mock_instance = MagicMock()
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_resp)
            MockOA.return_value = mock_instance

            client = OpenAIClient("gpt-4o", cost=0.01)
            result = await client.generate("show me users")

            assert result == "SELECT * FROM users"

    @pytest.mark.asyncio
    async def test_generate_no_api_key_returns_message(self) -> None:
        with patch("ke.services.inference.get_settings") as mock_settings:
            mock_settings.return_value.openai_api_key = ""
            mock_settings.return_value.openai_org_id = ""
            client = OpenAIClient("gpt-4o")
            result = await client.generate("test")
            assert "no openai api key" in result

    def test_model_name_property(self) -> None:
        client = OpenAIClient("gpt-4o")
        assert client.model_name == "gpt-4o"

    def test_cost_property(self) -> None:
        client = OpenAIClient("gpt-4o", cost=0.02)
        assert client.cost_per_query == 0.02


class TestMockClient:
    @pytest.mark.asyncio
    async def test_generate_extracts_user_request(self) -> None:
        client = MockClient()
        result = await client.generate("User Request: show me active users")
        assert "active users" in result
        assert result.startswith("SELECT * FROM mock_table")

    @pytest.mark.asyncio
    async def test_generate_falls_back_to_simple_pattern(self) -> None:
        client = MockClient()
        result = await client.generate("Generate a SQL query for: count orders")
        assert "count orders" in result

    @pytest.mark.asyncio
    async def test_generate_no_match(self) -> None:
        client = MockClient()
        result = await client.generate("just a random string without patterns")
        assert result == "SELECT * FROM mock_table WHERE query LIKE '%%'"

    def test_model_name_property(self) -> None:
        client = MockClient("my-mock")
        assert client.model_name == "my-mock"

    def test_cost_property(self) -> None:
        client = MockClient(cost=0.001)
        assert client.cost_per_query == 0.001


class TestInferenceFactory:
    def test_create_huggingface(self) -> None:
        with patch("ke.services.inference.get_settings") as mock_settings:
            mock_settings.return_value.hf_token = "test-token"
            mock_settings.return_value.openai_api_key = ""
            client = InferenceFactory.create("huggingface", "defog/sqlcoder-7b-2", 0.0001)
            assert isinstance(client, HFInferenceClient)
            assert client.model_name == "defog/sqlcoder-7b-2"
            assert client.cost_per_query == 0.0001

    def test_create_openai(self) -> None:
        with patch("ke.services.inference.get_settings") as mock_settings:
            mock_settings.return_value.hf_token = ""
            mock_settings.return_value.openai_api_key = "sk-test"
            client = InferenceFactory.create("openai", "gpt-4o", 0.01)
            assert isinstance(client, OpenAIClient)
            assert client.model_name == "gpt-4o"

    def test_create_mock(self) -> None:
        client = InferenceFactory.create("mock", "fallback", 0.0)
        assert isinstance(client, MockClient)
        assert client.model_name == "fallback"

    def test_create_unknown_provider_falls_to_mock(self) -> None:
        client = InferenceFactory.create("unknown_provider", "x", 0.0)
        assert isinstance(client, MockClient)

    def test_create_huggingface_no_model(self) -> None:
        client = InferenceFactory.create("huggingface", None, 0.0)
        assert isinstance(client, MockClient)

    def test_create_huggingface_no_token_falls_to_mock(self) -> None:
        with patch("ke.services.inference.get_settings") as mock_settings:
            mock_settings.return_value.hf_token = ""
            mock_settings.return_value.openai_api_key = ""
            client = InferenceFactory.create("huggingface", "test-model", 0.0)
            assert isinstance(client, MockClient)

    def test_create_openai_no_key_falls_to_mock(self) -> None:
        with patch("ke.services.inference.get_settings") as mock_settings:
            mock_settings.return_value.hf_token = ""
            mock_settings.return_value.openai_api_key = ""
            client = InferenceFactory.create("openai", "gpt-4o", 0.0)
            assert isinstance(client, MockClient)

    def test_register_custom_client(self) -> None:
        class CustomClient(MockClient):
            pass

        InferenceFactory.register("custom", CustomClient)
        client = InferenceFactory.create("custom", "test", 0.0)
        assert isinstance(client, CustomClient)
