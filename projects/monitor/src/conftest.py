import os
from unittest import mock
import pytest


@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(os.environ, {"DISABLE_CLOUD_WRITES": "true"}):
        yield


@pytest.fixture
def compute_manager(mock_settings_env_vars):
    from monorepo_cloud.compute import AWSComputeManager
    from monorepo_cloud.config import AWSConfig, load_aws_config

    aws_config: AWSConfig = load_aws_config()

    with mock.patch("app.interactor.event.aws.get_compute_manager") as mock_get_compute_manager:
        manager: AWSComputeManager = AWSComputeManager(config=aws_config)
        # manager.client = mock.MagicMock()
        mock_get_compute_manager.return_value = manager
        yield manager


@pytest.fixture
def db_manager(mock_settings_env_vars):
    from monorepo_cloud.db import AWSRDSManager
    from monorepo_cloud.config import AWSConfig, load_aws_config

    aws_config: AWSConfig = load_aws_config()

    with mock.patch("app.interactor.event.aws.get_db_manager") as mock_get_db_manager:
        manager: AWSRDSManager = AWSRDSManager(config=aws_config)
        # manager.client = mock.MagicMock()
        mock_get_db_manager.return_value = manager
        yield manager
