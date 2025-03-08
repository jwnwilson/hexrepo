from typing import Dict, Type
import uuid
from fastapi.testclient import TestClient
from pydantic import BaseModel
import pytest
from hexrepo_api.crud import CrudRouter

from app.domain.user import FeatureFlagDTO
from app.interactor.api.fastapi.api_versions.api_v1.routes.feature_flags import router_v1 as feature_flags_router


API_ENDPOINT_TEST_DATA = {
    "feature_flag": feature_flags_router,
}

def generateFeatureFlag():
    return FeatureFlagDTO(
        id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
        name="test",
        created_at="2024-08-30T08:06:10.591198",
        enabled=True
    )

TEST_DATA_FACTORY = {
    FeatureFlagDTO: generateFeatureFlag
}

def get_test_data(model: Type[BaseModel]) -> BaseModel:
    try:
        return TEST_DATA_FACTORY[model]()
    except KeyError:
        raise Exception(f"Test data factory not implemented for {model}")


@pytest.mark.parametrize("endpoint", API_ENDPOINT_TEST_DATA.keys())
def test_crud_create(client: TestClient, endpoint: Dict):
    router: CrudRouter = API_ENDPOINT_TEST_DATA[endpoint]
    create_payload = get_test_data(router.create_schema).model_dump()
    response = client.post(f"/api/v1/{endpoint}/", json=create_payload)
    assert response.status_code == 200
    reponse_data = response.json()
    for key, value in create_payload.items():
        assert reponse_data[key] == value
