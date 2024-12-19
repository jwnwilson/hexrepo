import os
from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient

from app.domain.example import ExampleDTO


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
