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
