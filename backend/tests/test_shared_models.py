from __future__ import annotations

from datetime import datetime
from typing import Any, cast

import pytest
from pydantic import ValidationError

from shared.models import (
    APIResponse,
    BaseSchema,
    ErrorDetail,
    ErrorResponse,
    MetaInfo,
    Page,
    PaginationParams,
    SortOrder,
    TenantScopedModel,
    TimestampMixin,
)


class TestBaseSchema:
    def test_frozen_by_default(self) -> None:
        class Example(BaseSchema):
            name: str

        instance = Example(name="test")
        with pytest.raises(ValidationError):
            cast(Any, instance).name = "changed"

    def test_extra_fields_forbidden(self) -> None:
        class Example(BaseSchema):
            name: str

        with pytest.raises(ValidationError):
            Example(name="test", extra_field="should_fail")  # type: ignore[call-arg]

    def test_strip_whitespace(self) -> None:
        class Example(BaseSchema):
            name: str

        instance = Example(name="  hello  ")
        assert instance.name == "hello"

    def test_populate_by_name(self) -> None:
        class Example(BaseSchema):
            full_name: str

        instance = Example(full_name="test")
        assert instance.full_name == "test"


class TestTimestampMixin:
    def test_auto_populates_timestamps(self) -> None:
        class Example(TimestampMixin):
            name: str

        instance = Example(name="test")
        assert isinstance(instance.created_at, datetime)
        assert isinstance(instance.updated_at, datetime)

    def test_custom_timestamps(self) -> None:
        class Example(TimestampMixin):
            name: str

        dt = datetime(2026, 1, 1, 0, 0, 0)
        instance = Example(name="test", created_at=dt, updated_at=dt)
        assert instance.created_at == dt
        assert instance.updated_at == dt


class TestTenantScopedModel:
    def test_requires_tenant_id(self) -> None:
        with pytest.raises(ValidationError):
            TenantScopedModel()  # type: ignore[call-arg]

    def test_accepts_valid_tenant_id(self) -> None:
        instance = TenantScopedModel(tenant_id="tnt_001")
        assert instance.tenant_id == "tnt_001"

    def test_is_frozen(self) -> None:
        instance = TenantScopedModel(tenant_id="tnt_001")
        with pytest.raises(ValidationError):
            cast(Any, instance).tenant_id = "tnt_002"

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            TenantScopedModel(tenant_id="tnt_001", unknown="x")  # type: ignore[call-arg]


class TestSortOrder:
    def test_enum_values(self) -> None:
        assert SortOrder.ASC.value == "asc"
        assert SortOrder.DESC.value == "desc"

    def test_valid_string_coercion(self) -> None:
        assert SortOrder("asc") == SortOrder.ASC
        assert SortOrder("desc") == SortOrder.DESC

    def test_invalid_string_raises(self) -> None:
        with pytest.raises(ValueError):
            SortOrder("invalid")


class TestPaginationParams:
    def test_defaults(self) -> None:
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 50
        assert params.sort_by is None
        assert params.sort_order == SortOrder.ASC

    def test_offset_and_limit(self) -> None:
        params = PaginationParams(page=3, page_size=20)
        assert params.offset == 40
        assert params.limit == 20

    def test_page_must_be_positive(self) -> None:
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

    def test_page_size_range(self) -> None:
        with pytest.raises(ValidationError):
            PaginationParams(page_size=1000)

    def test_invalid_sort_order_raises(self) -> None:
        with pytest.raises(ValidationError):
            PaginationParams(sort_order="invalid")  # type: ignore[arg-type]


class TestPage:
    def test_total_pages_computation(self) -> None:
        page = Page(items=[1, 2, 3], total=25, page=1, page_size=10)
        assert page.total_pages == 3
        assert page.has_next is True
        assert page.has_prev is False

    def test_last_page(self) -> None:
        page = Page(items=[], total=25, page=3, page_size=10)
        assert page.total_pages == 3
        assert page.has_next is False
        assert page.has_prev is True

    def test_empty_results(self) -> None:
        page = Page(items=[], total=0, page=1, page_size=10)
        assert page.total_pages == 1
        assert page.has_next is False
        assert page.has_prev is False

    def test_single_page(self) -> None:
        page = Page(items=[1], total=1, page=1, page_size=10)
        assert page.total_pages == 1
        assert page.has_next is False
        assert page.has_prev is False


class TestMetaInfo:
    def test_defaults(self) -> None:
        meta = MetaInfo()
        assert meta.request_id == ""
        assert meta.took_ms == 0.0
        assert meta.api_version == "1.0.0"
        assert meta.pagination is None

    def test_with_pagination(self) -> None:
        page = Page(items=[], total=0, page=1, page_size=10)
        meta = MetaInfo(pagination=page)
        assert meta.pagination is not None
        assert meta.pagination.total_pages == 1


class TestErrorDetail:
    def test_required_fields(self) -> None:
        detail = ErrorDetail(code="ERR-001", message="Something went wrong")
        assert detail.code == "ERR-001"
        assert detail.message == "Something went wrong"
        assert detail.details == {}
        assert detail.request_id == ""
        assert detail.docs_url == ""

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            ErrorDetail(code="ERR-001", message="err", extra="x")  # type: ignore[call-arg]


class TestErrorResponse:
    def test_creates_error_response(self) -> None:
        detail = ErrorDetail(code="ERR-001", message="Not found")
        response = ErrorResponse(error=detail)
        assert response.status == "error"
        assert response.error.code == "ERR-001"
        assert response.error.message == "Not found"

    def test_serialization(self) -> None:
        detail = ErrorDetail(code="ERR-001", message="Fail")
        response = ErrorResponse(error=detail)
        data = response.model_dump(by_alias=True)
        assert data["status"] == "error"
        assert data["error"]["code"] == "ERR-001"


class TestAPIResponse:
    def test_string_data(self) -> None:
        response = APIResponse[str](data="hello")
        assert response.status == "ok"
        assert response.data == "hello"
        assert response.meta.api_version == "1.0.0"

    def test_dict_data(self) -> None:
        response = APIResponse[dict[str, str]](data={"key": "value"})
        assert response.data == {"key": "value"}

    def test_list_data(self) -> None:
        response = APIResponse[list[int]](data=[1, 2, 3])
        assert response.data == [1, 2, 3]

    def test_model_data(self) -> None:
        class Item(BaseSchema):
            id: str

        item = Item(id="abc")
        response = APIResponse[Item](data=item)
        assert response.data.id == "abc"

    def test_serialization_round_trip(self) -> None:
        response = APIResponse[str](data="test", meta=MetaInfo(request_id="req_001"))
        data = response.model_dump()
        assert data["status"] == "ok"
        assert data["data"] == "test"
        assert data["meta"]["request_id"] == "req_001"

    def test_can_disable_extra_check_for_polymorphism(self) -> None:
        response = APIResponse[Any](data={"anything": True})
        data = response.model_dump()
        assert data["data"]["anything"] is True
