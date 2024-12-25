import json
from datetime import datetime
from unittest import mock

import pytest


@pytest.fixture
def mock_current_time():
    with mock.patch("app.interactor.event.aws.current_time") as mock_current_time:
        mock_current_time.return_value = datetime.strptime(
            "2022-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
        )
        yield mock_current_time


@pytest.fixture
def compute_manager():
    from monorepo_cloud.compute import AWSComputeManager
    from monorepo_cloud.config import AWSConfig, load_aws_config

    aws_config: AWSConfig = load_aws_config()

    mock_compute_data: str
    with open("src/tests/test_data/mock_compute_data.json") as f:
        mock_compute_data = json.loads(f.read())

    with mock.patch(
        "app.interactor.event.aws.get_compute_manager"
    ) as mock_get_compute_manager:
        manager: AWSComputeManager = AWSComputeManager(config=aws_config)
        manager.client = mock.MagicMock()
        manager.client.describe_instances.return_value = mock_compute_data
        mock_get_compute_manager.return_value = manager
        yield manager


@pytest.fixture
def db_manager():
    from monorepo_cloud.config import AWSConfig, load_aws_config
    from monorepo_cloud.db import AWSRDSManager

    aws_config: AWSConfig = load_aws_config()

    mock_db_data: str
    with open("src/tests/test_data/mock_db_data.json") as f:
        mock_db_data = json.loads(f.read())

    with mock.patch("app.interactor.event.aws.get_db_manager") as mock_get_db_manager:
        manager: AWSRDSManager = AWSRDSManager(config=aws_config)
        manager.client = mock.MagicMock()
        manager.client.describe_db_instances.return_value = mock_db_data
        mock_get_db_manager.return_value = manager
        yield manager
