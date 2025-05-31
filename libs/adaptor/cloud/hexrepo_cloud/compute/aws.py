import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import boto3
from mypy_boto3_ec2.type_defs import InstanceTypeDef

from hexrepo_cloud.config import AWSConfig

if TYPE_CHECKING:
    from mypy_boto3_ec2.client import EC2Client
    from mypy_boto3_ecs.client import ECSClient

logger = logging.getLogger()


class AWSEcsManager:
    def __init__(self, config: AWSConfig):
        self.config: AWSConfig = config
        self.client: ECSClient = boto3.client("ecs", region_name=self.config.AWS_REGION)

    def get_cluster_id(self, cluster_name: str) -> str:
        """Get the cluster ID for a given cluster name."""
        response = self.client.describe_clusters(clusters=[cluster_name])
        if not response["clusters"]:
            raise ValueError(f"Cluster {cluster_name} not found")
        return response["clusters"][0]["clusterArn"]

    def get_task_id(self, cluster_name: str, service_name: str) -> str:
        """Get the task ID for a given service in a cluster."""
        response = self.client.list_tasks(
            cluster=cluster_name, serviceName=service_name, desiredStatus="RUNNING"
        )
        if not response["taskArns"]:
            raise ValueError(f"No running tasks found for service {service_name}")
        return response["taskArns"][0].split("/")[-1]

    def execute_command(self, cluster_name: str, task_id: str, command: str) -> None:
        """Execute a command on an ECS task."""
        self.client.execute_command(
            cluster=cluster_name, task=task_id, command=command, interactive=True
        )


class AWSEc2Manager:
    def __init__(self, config: AWSConfig):
        self.config: AWSConfig = config
        self.client: EC2Client = boto3.client("ec2", region_name=self.config.AWS_REGION)

    def get_instances(
        self, state: Optional[str] = None, tags: Optional[Dict[str, Any]] = None
    ) -> List[InstanceTypeDef]:
        filters: List[Dict[str, Any]] = []
        tags = tags or {}
        for tag in tags:
            if isinstance(tags[tag], List):
                filters.append({"Name": "tag:" + tag, "Values": tags[tag]})
            else:
                filters.append({"Name": "tag:" + tag, "Values": [tags[tag]]})

        logger.info(f"Getting instances with filters: {filters}")
        instance_data = self.client.describe_instances(Filters=filters)  # type: ignore
        instancelist: List[InstanceTypeDef] = []
        for reservation in instance_data["Reservations"]:
            for instance in reservation["Instances"]:
                if not state:
                    instancelist.append(instance)
                elif instance["State"]["Name"].lower() == state.lower():
                    instancelist.append(instance)

        logger.info(f"Found {len(instancelist)} instances")
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
    def instance_tags_to_dict(cls, instance: InstanceTypeDef) -> Dict[str, str]:
        return {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
