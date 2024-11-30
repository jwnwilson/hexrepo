from datetime import datetime
from typing import Any, Dict, Optional
from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from monorepo_db.exception import RecordNotFound
from monorepo_db.interface import UOW, PaginatedData, Repository
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from monorepo_api.crud import CrudRouter


class MockCreateSchema(BaseModel):
    name: str


class MockUpdateSchema(BaseModel):
    name: str


class MockResponseSchema(BaseModel):
    id: UUID
    name: str
    created_at: datetime


class MockResponseFactory(ModelFactory):  # type: ignore
    __model__ = MockResponseSchema


mock_responses = MockResponseFactory.batch(3)


class MockRepository(Repository):
    def __init__(self) -> None:
        self.data = mock_responses

    def create(self, obj_in: Any) -> Any:
        return MockResponseSchema(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            name=obj_in.name,
            created_at=datetime.strptime(
                "2024-08-30T08:06:10.591198", "%Y-%m-%dT%H:%M:%S.%f"
            ),
        )

    def read(self, id: UUID) -> Any:
        if id == UUID("00000000-0000-0000-0000-000000000000"):
            raise RecordNotFound("Record not found")
        return MockResponseSchema(
            id=id,
            name="test",
            created_at=datetime.strptime(
                "2024-08-30T08:06:10.591198", "%Y-%m-%dT%H:%M:%S.%f"
            ),
        )

    def read_multi(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        page_number: int = 1,
        order_by: str = "-created_at",
    ) -> PaginatedData[Any]:
        results = sorted(
            self.data,
            key=lambda x: getattr(x, order_by.lstrip("-")),
            reverse=(order_by.startswith("-")),
        )
        start = (page_number - 1) * page_size
        end = start + page_size
        return PaginatedData(results=results, total=len(self.data))

    def update(self, id: UUID, obj_in: Any, merge_objects: bool = False) -> Any:
        return MockResponseSchema(
            id=id,
            name=obj_in.name,
            created_at=datetime.strptime(
                "2024-08-30T08:06:10.591198", "%Y-%m-%dT%H:%M:%S.%f"
            ),
        )

    def delete(self, id: UUID) -> None:
        if id == UUID("00000000-0000-0000-0000-000000000000"):
            raise RecordNotFound("Record not found")
        return


class MockUOW(UOW):
    repository: Repository = MockRepository()

    @property
    def session(self) -> Any:
        return Mock()


@pytest.fixture
def client() -> TestClient:
    def get_repos() -> UOW:
        return MockUOW(db_url="")

    router = CrudRouter(
        db_dependency=get_repos,
        repository="repository",
        response_schema=MockResponseSchema,
        methods=["CREATE", "READ", "UPDATE", "DELETE"],
        create_schema=MockCreateSchema,
        update_schema=MockUpdateSchema,
    )
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_initialization() -> None:
    def get_repos() -> UOW:
        return MockUOW(db_url="")

    router = CrudRouter(
        db_dependency=get_repos,
        repository="repository",
        response_schema=MockResponseSchema,
        methods=["CREATE", "READ", "UPDATE", "DELETE"],
        create_schema=MockCreateSchema,
        update_schema=MockUpdateSchema,
    )
    assert router.db_dependency == get_repos
    assert router.repository == "repository"
    assert router.response_schema == MockResponseSchema
    assert router.create_schema == MockCreateSchema
    assert router.update_schema == MockUpdateSchema


def test_create_route(client: TestClient) -> None:
    response = client.post("/", json={"name": "test"})
    assert response.status_code == 200
    assert response.json() == {
        "id": "12345678-1234-5678-1234-567812345678",
        "name": "test",
        "created_at": "2024-08-30T08:06:10.591198",
    }


def test_read_route(client: TestClient) -> None:
    response = client.get("/12345678-1234-5678-1234-567812345678")
    assert response.status_code == 200
    assert response.json() == {
        "id": "12345678-1234-5678-1234-567812345678",
        "name": "test",
        "created_at": "2024-08-30T08:06:10.591198",
    }


def test_read_route_not_found_exc(client: TestClient) -> None:
    # with pytest.raises(RecordNotFound):
    response = client.get("/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_route(client: TestClient) -> None:
    response = client.patch(
        "/12345678-1234-5678-1234-567812345678", json={"name": "updated"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "12345678-1234-5678-1234-567812345678",
        "name": "updated",
        "created_at": "2024-08-30T08:06:10.591198",
    }


def test_delete_route(client: TestClient) -> None:
    response = client.delete("/12345678-1234-5678-1234-567812345678")
    assert response.status_code == 204

    response = client.delete("/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_read_multi_route_with_ordering_asc(client: TestClient) -> None:
    response = client.get("/?order_by=name")
    assert response.status_code == 200
    data = response.json()
    results = [MockResponseSchema(**d) for d in data["results"]]
    assert results == sorted(mock_responses, key=lambda m: m.name)


def test_read_multi_route_with_ordering_desc(client: TestClient) -> None:
    response = client.get("/?order_by=-name")
    assert response.status_code == 200
    data = response.json()
    results = [MockResponseSchema(**d) for d in data["results"]]
    assert results == sorted(mock_responses, key=lambda m: m.name, reverse=True)
