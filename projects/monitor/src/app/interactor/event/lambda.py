import json
from typing import Any, List
import os

from monorepo_cloud.compute import AWSComputeManager
from monorepo_cloud.config import AWSConfig, load_aws_config
from monorepo_cloud.db import AWSRDSManager


def handler(event, context):
    aws_config: AWSConfig = load_aws_config()
    compute_manager: AWSComputeManager = AWSComputeManager(config=aws_config)
    rds_manager: AWSRDSManager = AWSRDSManager(config=aws_config)
    compute_instances: List[Any] = compute_manager.get_instances(tags={"": ""})
    db_instances: List[Any] = rds_manager.get_db_ids(tags={"": ""})

    # Start instances that should be started

    # Stop instances that should be stopped
