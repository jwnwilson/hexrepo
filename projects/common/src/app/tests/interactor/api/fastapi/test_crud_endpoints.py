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
def test_crud_create(client: TestClient, endpoint: Dict, create_environments):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    create_payload = json.loads(get_test_data(router.create_schema).model_dump_json())
    response = client.post(f"/api/v1/{endpoint}/", json=create_payload)
    assert response.status_code == 200
    reponse_data = response.json()
    if endpoint == "feature_flag":
        assert reponse_data["name"] == create_payload["name"]
        assert all(
            [
                env["enabled"] == create_payload["enabled"]
                for env in reponse_data["environments"]
            ]
        )
    else:
        for key, value in create_payload.items():
            if key == "id":
                continue
            assert reponse_data[key] == value


@pytest.mark.parametrize("endpoint", API_ENDPOINT_TEST_DATA.keys())
def test_crud_read_many(
    client: TestClient, test_data_generator, endpoint: Dict, create_environments
):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    if endpoint == "feature_flag":
        create_dto = get_test_data(router.create_schema)
    else:
        create_dto = get_test_data(router.response_schema)
    test_data = test_data_generator(create_dto)
    response = client.get(f"/api/v1/{endpoint}/")
    assert response.status_code == 200
    reponse_data = response.json()
    assert reponse_data["results"][0] == json.loads(test_data.model_dump_json())


@pytest.mark.parametrize("endpoint", API_ENDPOINT_TEST_DATA.keys())
def test_crud_read_single(
    client: TestClient, test_data_generator, endpoint: Dict, create_environments
):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    if endpoint == "feature_flag":
        create_dto = get_test_data(router.create_schema)
    else:
        create_dto = get_test_data(router.response_schema)
    test_data = test_data_generator(create_dto)
    response = client.get(f"/api/v1/{endpoint}/{test_data.id}")
    assert response.status_code == 200
    reponse_data = response.json()
    assert reponse_data == json.loads(test_data.model_dump_json())


@pytest.mark.parametrize("endpoint", API_ENDPOINT_TEST_DATA.keys())
def test_crud_update(
    uow, client: TestClient, test_data_generator, endpoint: Dict, create_environments
):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    # Create a new record
    if endpoint == "feature_flag":
        create_payload = get_test_data(router.create_schema)
    else:
        create_payload = get_test_data(router.response_schema)
    create_record = test_data_generator(create_payload)
    update_id = create_record.id
    update_payload = get_test_data(router.update_schema)
    update_payload.id = update_id
    update_payload_dict: Dict = json.loads(update_payload.model_dump_json())
    response = client.patch(f"/api/v1/{endpoint}/{update_id}", json=update_payload_dict)
    assert response.status_code == 200, response.json()
    reponse_data = response.json()
    for key, value in update_payload_dict.items():
        assert reponse_data[key] == value


@pytest.mark.parametrize("endpoint", API_ENDPOINT_TEST_DATA.keys())
def test_crud_delete(
    client: TestClient, test_data_generator, endpoint: Dict, create_environments
):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    if endpoint == "feature_flag":
        create_dto = get_test_data(router.create_schema)
    else:
        create_dto = get_test_data(router.response_schema)
    test_data = test_data_generator(create_dto)
    response = client.delete(f"/api/v1/{endpoint}/{test_data.id}")
    assert response.status_code == 204
