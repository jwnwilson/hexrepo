from datetime import datetime
from typing import Any, Dict

from hexrepo_cloud.compute.aws import AWSComputeManager
from hexrepo_cloud.db.aws import AWSRDSManager

from app.interactor.event.aws import handler


def test_monitor_no_change(
    compute_manager: AWSComputeManager, db_manager: AWSRDSManager, mock_current_time
):
    mock_current_time.return_value = datetime.strptime(
        "2025-01-01T12:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
    )

    handler(event={}, context={})

    assert compute_manager.client.start_instances.called is False
    assert compute_manager.client.stop_instances.called is False


def test_monitor_starts_instances(
    compute_manager: AWSComputeManager, db_manager: AWSRDSManager, mock_current_time
):
    instance_data: Dict[str, Any] = compute_manager.client.describe_instances()
    instance_data["Reservations"][0]["Instances"][0]["State"]["Name"] = "stopped"
    mock_current_time.return_value = datetime.strptime(
        "2025-01-01T12:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
    )

    handler(event={}, context={})

    assert compute_manager.client.start_instances.called is True
    assert compute_manager.client.stop_instances.called is False


def test_monitor_stops_instances(
    compute_manager: AWSComputeManager, db_manager: AWSRDSManager, mock_current_time
):
    instance_data: Dict[str, Any] = compute_manager.client.describe_instances()
    instance_data["Reservations"][0]["Instances"][0]["State"]["Name"] = "running"
    mock_current_time.return_value = datetime.strptime(
        "2025-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"
    )

    handler(event={}, context={})

    assert compute_manager.client.start_instances.called is False
    assert compute_manager.client.stop_instances.called is True
