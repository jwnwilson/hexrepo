from app.interactor.event.aws import handler
from monorepo_cloud.compute.aws import AWSComputeManager
from monorepo_cloud.db.aws import AWSRDSManager


def test_monitor_starts_instances(compute_manager: AWSComputeManager, db_manager: AWSRDSManager):
    handler(event={}, context={})

    assert compute_manager.client.start_instances.called
    assert compute_manager.client.stop_instances.called
