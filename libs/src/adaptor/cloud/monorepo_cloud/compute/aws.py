import logging
import os
from typing import Any, Dict, List, Optional

import boto3

from monorepo_cloud.config import AWSConfig
from mypy_boto3_ec2.client import EC2Client
    

logger = logging.getLogger()


class AWSComputeManager:
    def __init__(self, config: AWSConfig):
        self.config: AWSConfig = config
        self.client: EC2Client = boto3.client("ec2", region_name=self.config.AWS_REGION)
        self.disable_writes: bool = os.environ.get("DISABLE_CLOUD_WRITES", "false") == "true"

    def get_instances(
        self, state: Optional[str] = None, tags: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        filters: List[Dict[str, Any]] = []
        tags = tags or {}
        for tag in tags:
            if isinstance(tags[tag], List):
                filters.append({"Name": "tag:" + tag, "Values": tags[tag]})
            else:
                filters.append({"Name": "tag:" + tag, "Values": [tags[tag]]})

        instance_data = self.client.describe_instances(Filters=filters)
        instancelist = []
        for reservation in instance_data["Reservations"]:
            for instance in reservation["Instances"]:
                if not state:
                    instancelist.append(instance["InstanceId"])
                elif instance["State"]["Name"].lower() == state.lower():
                    instancelist.append(instance["InstanceId"])
        return instancelist

    def start_instances(self, instance_ids: List[str]) -> List[str]:
        if self.disable_writes:
            logger.info("Skipping starting instances due to DISABLE_CLOUD_WRITES")
            return instance_ids
        
        self.client.start_instances(InstanceIds=instance_ids)
        logger.info("Started instances: " + str(instance_ids))

        return instance_ids

    def stop_instances(self, instance_ids: List[str]) -> List[str]:
        if self.disable_writes:
            logger.info("Skipping stopped instances due to DISABLE_CLOUD_WRITES")
            return instance_ids
        
        self.client.stop_instances(InstanceIds=instance_ids)
        logger.info("Stopped instances: " + str(instance_ids))

        return instance_ids
