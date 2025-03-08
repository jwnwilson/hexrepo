from typing import Dict

import pytest
from fastapi.testclient import TestClient
from hexrepo_api.crud import CrudRouter

from app.interactor.api.fastapi.api_versions.api_v1.api import (
    feature_flags_router,
    users_router,
)

from .factory import get_test_data

API_ENDPOINT_TEST_DATA = {
    "feature_flag": feature_flags_router,
    "user": users_router,
}


@pytest.mark.parametrize("endpoint", API_ENDPOINT_TEST_DATA.keys())
def test_crud_create(client: TestClient, endpoint: Dict):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    create_payload = get_test_data(router.create_schema).model_dump()
    response = client.post(f"/api/v1/{endpoint}/", json=create_payload)
    assert response.status_code == 200
    reponse_data = response.json()
    for key, value in create_payload.items():
        assert reponse_data[key] == value


@pytest.mark.parametrize("endpoint", API_ENDPOINT_TEST_DATA.keys())
def test_crud_read_many(client: TestClient, test_data_generator, endpoint: Dict):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    record = test_data_generator(payload=router.create_schema)
    response = client.get(f"/api/v1/{endpoint}/")
    assert response.status_code == 200
    reponse_data = response.json()
    assert reponse_data["results"] == record.model_dump()
