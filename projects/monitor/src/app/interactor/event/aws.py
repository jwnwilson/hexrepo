import datetime
import logging
from typing import Any, Dict, List, Tuple

from monorepo_cloud.compute import AWSComputeManager
from monorepo_cloud.config import AWSConfig, load_aws_config
from monorepo_cloud.db import AWSRDSManager

logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger(__name__)


def current_time() -> datetime.datetime:
    return datetime.datetime.now()


def get_compute_manager(aws_config: AWSConfig) -> AWSComputeManager:
    return AWSComputeManager(config=aws_config)


def get_db_manager(aws_config: AWSRDSManager) -> AWSRDSManager:
    return AWSRDSManager(config=aws_config)


def instance_tag_to_datetime(
    tags: Dict[str, str],
) -> Tuple[datetime.datetime, datetime.datetime]:
    tag_start_hour: int = int(tags["StartTime"].split(":")[0])
    tag_start_minute: int = int(tags["StartTime"].split(":")[1])
    tag_stop_hour: int = int(tags["StopTime"].split(":")[0])
    tag_stop_minute: int = int(tags["StopTime"].split(":")[1])

    start_time: datetime.datetime = current_time()
    stop_time: datetime.datetime = current_time()
    start_time = start_time.replace(hour=tag_start_hour, minute=tag_start_minute)
    stop_time = stop_time.replace(hour=tag_stop_hour, minute=tag_stop_minute)

    return (start_time, stop_time)


def should_start_compute_instance(instance: Dict[str, Any]) -> bool:
    if instance["State"]["Name"] == "running":
        return False

    now: datetime.datetime = current_time()
    start_time: datetime.datetime
    stop_time: datetime.datetime
    try:
        start_time, stop_time = instance_tag_to_datetime(
            AWSComputeManager.instance_tags_to_dict(instance)
        )
    except Exception as e:
        logger.info(f"Invalid StartTime / StopTime tags: {e}")
        return False

    if start_time < now and now < stop_time:
        return True
    else:
        return False


def should_start_db_instance(instance: Dict[str, Any]) -> bool:
    if instance["DBInstanceStatus"] == "available":
        return False

    now: datetime.datetime = current_time()
    start_time: datetime.datetime
    stop_time: datetime.datetime
    try:
        start_time, stop_time = instance_tag_to_datetime(
            AWSRDSManager.instance_tags_to_dict(instance)
        )
    except Exception as e:
        logger.info(f"Invalid StartTime / StopTime tags: {e}")
        return False

    if start_time < now and now < stop_time:
        return True
    else:
        return False


def should_stop_compute_instance(instance: Any) -> bool:
    if instance["State"]["Name"] == "stopped":
        return False

    now: datetime.datetime = current_time()
    start_time: datetime.datetime
    stop_time: datetime.datetime
    start_time, stop_time = instance_tag_to_datetime(
        AWSComputeManager.instance_tags_to_dict(instance)
    )

    if now < start_time or stop_time < now:
        return True
    else:
        return False


def should_stop_db_instance(instance: Dict[str, Any]) -> bool:
    if instance["DBInstanceStatus"] == "stopped":
        return False

    now: datetime.datetime = current_time()
    start_time: datetime.datetime
    stop_time: datetime.datetime
    try:
        start_time, stop_time = instance_tag_to_datetime(
            AWSRDSManager.instance_tags_to_dict(instance)
        )
    except Exception as e:
        logger.info(f"Invalid StartTime / StopTime tags: {e}")
        return False

    if now < start_time or stop_time < now:
        return True
    else:
        return False


def handler(event, context):
    aws_config: AWSConfig = load_aws_config()
    compute_manager: AWSComputeManager = get_compute_manager(aws_config=aws_config)
    rds_manager: AWSRDSManager = get_db_manager(aws_config=aws_config)
    compute_instances: List[Any] = compute_manager.get_instances(
        tags={"Type": "bastion"}
    )
    db_instances: List[Any] = rds_manager.get_db_instances(
        tags={"Project": ["example"]}
    )

    # Start / stop compute instances
    for instance in compute_instances:
        if should_start_compute_instance(instance):
            logger.info(f"Starting compute instance: {instance['InstanceId']}")
            compute_manager.start_instances(instance_ids=[instance["InstanceId"]])
        elif should_stop_compute_instance(instance):
            logger.info(f"Stopping compute instance: {instance['InstanceId']}")
            compute_manager.stop_instances(instance_ids=[instance["InstanceId"]])
        else:
            logger.info(
                f"No action needed for compute instance: {instance['InstanceId']}"
            )

    # Stop / stop
    for instance in db_instances:
        if should_start_db_instance(instance):
            logger.info(f"Starting RDS instance: {instance['DBInstanceIdentifier']}")
            rds_manager.start_dbs(db_instance_ids=[instance["DBInstanceIdentifier"]])
        elif should_stop_db_instance(instance):
            logger.info(f"Stopping RDS instance: {instance['DBInstanceIdentifier']}")
            rds_manager.stop_rds(db_instance_ids=[instance["DBInstanceIdentifier"]])
        else:
            logger.info(
                f"No action needed for RDS instance: {instance['DBInstanceIdentifier']}"
            )
