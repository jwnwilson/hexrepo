import logging
import os
from typing import Any, Dict, List, Optional

import boto3
from mypy_boto3_ec2.client import EC2Client  # type: ignore

from monorepo_cloud.config import AWSConfig

logger = logging.getLogger()


class AWSComputeManager:
    def __init__(self, config: AWSConfig):
        self.config: AWSConfig = config
        self.client: EC2Client = boto3.client("ec2", region_name=self.config.AWS_REGION)

    def get_instances(
        self, state: Optional[str] = None, tags: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
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
                    instancelist.append(instance)
                elif instance["State"]["Name"].lower() == state.lower():
                    instancelist.append(instance)
        return instancelist

    def get_instances_ids(
        self, state: Optional[str] = None, tags: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        return [
            inst["InstanceId"] for inst in self.get_instances(state=state, tags=tags)
        ]

    def start_instances(self, instance_ids: List[str]) -> List[str]:
        self.client.start_instances(InstanceIds=instance_ids)
        logger.info("Started instances: " + str(instance_ids))

        return instance_ids

    def stop_instances(self, instance_ids: List[str]) -> List[str]:
        self.client.stop_instances(InstanceIds=instance_ids)
        logger.info("Stopped instances: " + str(instance_ids))

        return instance_ids

    @classmethod
    def instance_tags_to_dict(cls, instance: Dict[str, Any]) -> Dict[str, str]:
        return {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
