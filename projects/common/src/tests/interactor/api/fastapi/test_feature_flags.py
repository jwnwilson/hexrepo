import json

import pytest
from fastapi import status

from app.adaptor.db.sql.models.environment import EnvironmentTable


@pytest.fixture
def setup_environments(uow):
    """Fixture to create test environments in the database"""
    environments = [
        {"name": "dev", "config": {"type": "development"}},
        {"name": "staging", "config": {"type": "staging"}},
        {"name": "prod", "config": {"type": "production"}},
    ]

    for env in environments:
        environment = EnvironmentTable(**env)
        uow.session.add(environment)
    uow.session.commit()
    return environments


@pytest.fixture
def feature_flag_data():
    return {"name": "test_flag", "enabled": True}


@pytest.fixture
def feature_flag_env_data():
    return {"env": "dev", "enabled": True, "overrides": {"user_id": "123"}}


def test_create_feature_flag(client, feature_flag_data, setup_environments):
    """Test creating a new feature flag"""
    response = client.post("/api/v1/feature_flag/", json=feature_flag_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == feature_flag_data["name"]
    assert "id" in data
    assert isinstance(data["id"], str)


def test_get_feature_flag(client, feature_flag_data, setup_environments):
    """Test retrieving a feature flag by ID"""
    # First create a feature flag
    create_response = client.post("/api/v1/feature_flag/", json=feature_flag_data)
    flag_id = create_response.json()["id"]

    # Then retrieve it
    response = client.get(f"/api/v1/feature_flag/{flag_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == feature_flag_data["name"]
    assert data["id"] == flag_id


def test_update_feature_flag(client, feature_flag_data, setup_environments):
    """Test updating a feature flag"""
    # First create a feature flag
    create_response = client.post("/api/v1/feature_flag/", json=feature_flag_data)
    flag_id = create_response.json()["id"]

    # Update the flag
    updated_data = {"id": flag_id, "name": "updated_flag"}
    response = client.patch(f"/api/v1/feature_flag/{flag_id}", json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "updated_flag"


def test_delete_feature_flag(client, feature_flag_data, setup_environments):
    """Test deleting a feature flag"""
    # First create a feature flag
    create_response = client.post("/api/v1/feature_flag/", json=feature_flag_data)
    flag_id = create_response.json()["id"]

    # Delete the flag
    response = client.delete(f"/api/v1/feature_flag/{flag_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    get_response = client.get(f"/api/v1/feature_flag/{flag_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_get_feature_flags_endpoint(
    client, feature_flag_data, feature_flag_env_data, setup_environments
):
    """Test the custom get_feature_flags endpoint"""
    # Create a feature flag with environment
    client.post("/api/v1/feature_flag/", json=feature_flag_data)

    # Test get_flags endpoint
    flags = [feature_flag_data["name"]]
    response = client.get(
        "/api/v1/feature_flag/get_flags/",
        params={"flags": json.dumps(flags), "env": feature_flag_env_data["env"]},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == feature_flag_data["name"]
    assert data[0]["env"] == feature_flag_env_data["env"]
    assert data[0]["enabled"] == feature_flag_env_data["enabled"]


def test_get_feature_flags_nonexistent(client, setup_environments):
    """Test getting feature flags that don't exist"""
    flags = ["nonexistent_flag"]
    response = client.get(
        "/api/v1/feature_flag/get_flags/",
        params={"flags": json.dumps(flags), "env": "dev"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0


def test_get_feature_flags_multiple_envs(
    uow, client, feature_flag_data, setup_environments
):
    """Test feature flag behavior across multiple environments"""
    # Create a feature flag
    create_response = client.post("/api/v1/feature_flag/", json=feature_flag_data)
    flag_id = create_response.json()["id"]

    # Add multiple environments
    envs = [
        {"env": "dev", "enabled": True, "overrides": None},
        {"env": "staging", "enabled": False, "overrides": {"group": "beta"}},
        {"env": "prod", "enabled": True, "overrides": None},
    ]

    # Get existing feature flag envs and update them
    flag_response = client.get(f"/api/v1/feature_flag/{flag_id}")
    existing_envs = flag_response.json()["environments"]

    for env_data in envs:
        env_id = next(
            env["id"] for env in existing_envs if env["env"] == env_data["env"]
        )
        resp = client.patch(
            f"/api/v1/feature_flag_env/{env_id}",
            json={"enabled": env_data["enabled"], "overrides": env_data["overrides"]},
        )
        assert resp.status_code == status.HTTP_200_OK
    # Test each environment
    for env_data in envs:
        response = client.get(
            "/api/v1/feature_flag/get_flags/",
            params={
                "flags": json.dumps([feature_flag_data["name"]]),
                "env": env_data["env"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == feature_flag_data["name"]
        assert data[0]["env"] == env_data["env"]
        assert data[0]["enabled"] == env_data["enabled"]


def test_invalid_feature_flag_name(client, setup_environments):
    """Test creating a feature flag with invalid name"""
    invalid_data = {
        "name": "",  # Empty name
        "enabled": True,
    }
    response = client.post("/api/v1/feature_flag/", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
