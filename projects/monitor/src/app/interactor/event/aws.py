from typing import Any, List, Tuple
import datetime

from monorepo_cloud.compute import AWSComputeManager
from monorepo_cloud.config import AWSConfig, load_aws_config
from monorepo_cloud.db import AWSRDSManager


def instance_tag_to_datetime(instance: Any) -> Tuple[datetime.datetime, datetime.datetime]:
    tag_start_hour: int = int(instance["Tags"]["Start"]).split(":")[0]
    tag_start_minute: int = int(instance["Tags"]["Start"]).split(":")[1]
    tag_stop_hour: int = int(instance["Tags"]["Stop"]).split(":")[0]
    tag_stop_minute: int = int(instance["Tags"]["Stop"]).split(":")[1]
    
    start_time: datetime.datetime = datetime.datetime.now()
    stop_time: datetime.datetime = datetime.datetime.now()
    start_time.hour = tag_start_hour
    start_time.minute = tag_start_minute
    stop_time.hour = tag_stop_hour
    stop_time.minute = tag_stop_minute

    return (start_time, stop_time)


def should_start_instance(instance: Any) -> bool:
    if instance["State"]["Name"] == "running":
        return False
    
    now: datetime.datetime = datetime.datetime.now()
    start_time: datetime.datetime
    stop_time: datetime.datetime
    start_time, stop_time = instance_tag_to_datetime(instance)

    if start_time < now and now < stop_time:
        return True
    else:
        return False
    

def should_stop_instance(instance: Any) -> bool:
    if instance["State"]["Name"] == "stopped":
        return False
    
    now: datetime.datetime = datetime.datetime.now()
    start_time: datetime.datetime
    stop_time: datetime.datetime
    start_time, stop_time = instance_tag_to_datetime(instance)

    if now < start_time or stop_time < now:
        return True
    else:
        return False


def get_compute_manager(aws_config: AWSConfig) -> AWSComputeManager:
    return AWSComputeManager(config=aws_config)


def get_db_manager(aws_config: AWSRDSManager) -> AWSRDSManager:
    return AWSRDSManager(config=aws_config)


def handler(event, context):
    aws_config: AWSConfig = load_aws_config()
    compute_manager: AWSComputeManager = get_compute_manager(config=aws_config)
    rds_manager: AWSRDSManager = get_db_manager(config=aws_config)
    breakpoint()
    compute_instances: List[Any] = compute_manager.get_instances(tags={"Type": "Bastion"})
    db_instances: List[Any] = rds_manager.get_db_ids(tags={"Project": ["example"]})
    
    # Start / stop compute instances
    for instance in compute_instances:
        if should_start_instance(instance):
            compute_manager.start_instances(instance_ids=[instance["InstanceId"]])
        elif should_stop_instance(instance):
            compute_manager.stop_instances(instance_ids=[instance["InstanceId"]])

    # Stop / stop 
    for instance in db_instances:
        if should_start_instance(instance):
            rds_manager.start_dbs(instance_ids=[instance])
        elif should_stop_instance(instance):
            rds_manager.stop_rds(instance_ids=[instance])
