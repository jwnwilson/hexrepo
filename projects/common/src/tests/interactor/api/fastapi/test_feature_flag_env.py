from fastapi import status


def test_create_feature_flag_env(
    client, feature_flag_data, feature_flag_env_data, setup_environments
):
    """Test creating a new feature flag environment"""
    # First create a feature flag
    client.post("/api/v1/feature_flag/", json=feature_flag_data)

    # Create environment for the feature flag
    response = client.get("/api/v1/feature_flag_env/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["results"]) == 3
    assert data["results"][0]["env"] == "dev"
    assert data["results"][0]["enabled"] is True
    assert data["results"][0]["overrides"] is None
    assert isinstance(data["results"][0]["id"], str)


def test_get_feature_flag_env(
    client, feature_flag_data, feature_flag_env_data, setup_environments
):
    """Test retrieving a feature flag environment by ID"""
    # Create feature flag and environment
    create_response = client.post("/api/v1/feature_flag/", json=feature_flag_data)
    flag_id = create_response.json()["id"]

    env_data = {**feature_flag_env_data, "feature_flag_id": flag_id}
    create_env_response = client.post("/api/v1/feature_flag_env/", json=env_data)
    env_id = create_env_response.json()["id"]

    # Get the environment
    response = client.get(f"/api/v1/feature_flag_env/{env_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["env"] == feature_flag_env_data["env"]
    assert data["enabled"] == feature_flag_env_data["enabled"]
    assert data["overrides"] == feature_flag_env_data["overrides"]


def test_update_feature_flag_env(
    client, feature_flag_data, feature_flag_env_data, setup_environments
):
    """Test updating a feature flag environment"""
    # Create feature flag and environment
    create_response = client.post("/api/v1/feature_flag/", json=feature_flag_data)
    flag_id = create_response.json()["id"]

    env_data = {**feature_flag_env_data, "feature_flag_id": flag_id}
    create_env_response = client.post("/api/v1/feature_flag_env/", json=env_data)
    env_id = create_env_response.json()["id"]

    # Update the environment
    updated_data = {
        "id": env_id,
        "env": "staging",
        "enabled": False,
        "overrides": {"group": "beta"},
    }
    response = client.put(f"/api/v1/feature_flag_env/{env_id}", json=updated_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["env"] == "staging"
    assert data["enabled"] is False
    assert data["overrides"] == {"group": "beta"}


def test_delete_feature_flag_env(
    client, feature_flag_data, feature_flag_env_data, setup_environments
):
    """Test deleting a feature flag environment"""
    # Create feature flag and environment
    create_response = client.post("/api/v1/feature_flag/", json=feature_flag_data)
    flag_id = create_response.json()["id"]

    env_data = {**feature_flag_env_data, "feature_flag_id": flag_id}
    create_env_response = client.post("/api/v1/feature_flag_env/", json=env_data)
    env_id = create_env_response.json()["id"]

    # Delete the environment
    response = client.delete(f"/api/v1/feature_flag_env/{env_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    get_response = client.get(f"/api/v1/feature_flag_env/{env_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_create_duplicate_env(
    client, feature_flag_data, feature_flag_env_data, setup_environments
):
    """Test creating a duplicate environment for a feature flag"""
    # Create feature flag
    create_response = client.post("/api/v1/feature_flag/", json=feature_flag_data)
    flag_id = create_response.json()["id"]

    # Create first environment
    env_data = {**feature_flag_env_data, "feature_flag_id": flag_id}
    client.post("/api/v1/feature_flag_env/", json=env_data)

    # Try to create duplicate environment
    response = client.post("/api/v1/feature_flag_env/", json=env_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
