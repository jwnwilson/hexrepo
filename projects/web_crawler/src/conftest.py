import os
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient

from app.interactor.api.fastapi.dependencies import StubbedUOW
from monorepo_db import UOW

from app.domain.example import ExampleDTO

@pytest.fixture
def uow() -> Generator[UOW, None, None]:
    yield StubbedUOW(db_url="test")

@pytest.fixture
def client(uow):
    from app.interactor.api.fastapi import app
    from app.interactor.api.fastapi.dependencies import get_uow

    def get_uow_override():
        yield uow

    app.dependency_overrides[get_uow] = get_uow_override
    return TestClient(app)


@pytest.fixture
def example_data():
    return {
        "name": "test",
        "url": "https://test.com",
        "location": "test location",
    }


@pytest.fixture
def created_example(client: TestClient, example_data) -> ExampleDTO:
    response = client.post("/api/v1/example/", json=example_data)
    return ExampleDTO(**response.json())

