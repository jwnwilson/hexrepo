import logging
import os
from typing import Any, Dict, List, Optional

import boto3 

from ..config import AWSConfig
from mypy_boto3_rds.client import RDSClient

logger = logging.getLogger(__name__)


class AWSRDSManager:
    def __init__(self, config: AWSConfig):
        self.config: AWSConfig = config
        self.client: RDSClient = boto3.client("rds", self.config.AWS_REGION)
        self.disable_writes: bool = os.environ.get("DISABLE_CLOUD_WRITES", "false") == "true"

    def instance_has_tags(self, instance: Dict[str, Any], tags: Dict[str, str]) -> bool:
        instance_tags: Dict[str, str] = {
            tag["Key"]: tag["Value"] for tag in instance["TagList"]
        }
        for tag in tags:
            if tag not in instance_tags:
                return False
            if instance_tags[tag] != tags[tag]:
                return False
        return True

    def get_db_ids(
        self, state: Optional[str] = None, tags: Optional[Dict[str, str]] = None
    ) -> List[str]:
        filters: List[Dict[str, Any]] = []
        tags = tags or {}
        for tag in tags:
            filters.append({"Name": "tag:" + tag, "Values": [tags[tag]]})

        db_instances = []
        db_instance_info = self.client.describe_db_instances()
        for each_db in db_instance_info["DBInstances"]:
            if not self.instance_has_tags(each_db, tags):
                continue
            if state and each_db["DBInstanceStatus"].lower() == state.lower():
                db_instances.append(each_db["DBInstanceIdentifier"])
            else:
                db_instances.append(each_db["DBInstanceIdentifier"])

        return db_instances

    def get_rds_host(self, tags: Optional[Dict[str, str]] = None) -> str:
        db_instance_ids: List[str] = self.get_db_ids(tags=tags)
        if len(db_instance_ids) > 1:
            raise ValueError("Multiple RDS instances found")
        db_instance_info = self.client.describe_db_instances(
            DBInstanceIdentifier=db_instance_ids[0]
        )
        return db_instance_info["DBInstances"][0]["Endpoint"]["Address"]  # type: ignore

    def start_dbs(self, db_instance_ids: List[str]) -> List[str]:
        if self.disable_writes:
            logger.info("Skipping starting instances due to DISABLE_CLOUD_WRITES")
            return db_instance_ids
        
        for db_instance_id in db_instance_ids:
            self.client.start_db_instance(DBInstanceIdentifier=db_instance_id)
            logger.info(f"Started RDS instance: {db_instance_id}")
        return db_instance_ids

    def stop_rds(self, db_instance_ids: List[str]) -> List[str]:
        if self.disable_writes:
            logger.info("Skipping stopping instances due to DISABLE_CLOUD_WRITES")
            return db_instance_ids
        
        for db_instance_id in db_instance_ids:
            self.client.stop_db_instance(DBInstanceIdentifier=db_instance_id)
            logger.info(f"Stopped RDS instance: {db_instance_id}")
        return db_instance_ids
