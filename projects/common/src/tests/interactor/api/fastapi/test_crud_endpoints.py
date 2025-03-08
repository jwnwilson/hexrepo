import json
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from hexrepo_api.crud import CrudRouter

from app.interactor.api.fastapi.api_versions.api_v1.api import (
    company_router,
    feature_flags_router,
    groups_router,
    permissions_router,
    users_router,
)

from ..factory import get_test_data

API_ENDPOINT_TEST_DATA = {
    "feature_flag": feature_flags_router,
    "company": company_router,
    "group": groups_router,
    "user": users_router,
    "permission": permissions_router,
}


@pytest.mark.parametrize("endpoint", API_ENDPOINT_TEST_DATA.keys())
def test_crud_create(client: TestClient, endpoint: Dict):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    create_payload = json.loads(get_test_data(router.create_schema).model_dump_json())
    response = client.post(f"/api/v1/{endpoint}/", json=create_payload)
    assert response.status_code == 200
    reponse_data = response.json()
    for key, value in create_payload.items():
        if key == "id":
            continue
        assert reponse_data[key] == value


@pytest.mark.parametrize("endpoint", API_ENDPOINT_TEST_DATA.keys())
def test_crud_read_many(client: TestClient, test_data_generator, endpoint: Dict):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    create_dto = get_test_data(router.response_schema)
    test_data = test_data_generator(create_dto)
    response = client.get(f"/api/v1/{endpoint}/")
    assert response.status_code == 200
    reponse_data = response.json()
    assert reponse_data["results"][0] == json.loads(test_data.model_dump_json())
