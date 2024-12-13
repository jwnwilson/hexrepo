import logging
from typing import Dict, List, Optional

import boto3  # type: ignore

from ..config import AWSConfig

logger = logging.getLogger(__name__)


class AWSRDSManager:
    def __init__(self, config: AWSConfig):
        self.config: AWSConfig = config
        self.client = boto3.client("rds", self.config.AWS_REGION)

    def get_db_ids(self, state: Optional[str] = None, tags: Optional[Dict[str,str]] = None) -> List[str]:
        db_instance_info = self.client.describe_db_instances()

        db_instances = []
        for each_db in db_instance_info["DBInstances"]:
            if not state:
                db_instances.append(each_db["DBInstanceIdentifier"])
            elif each_db["DBInstanceStatus"].lower() == state.lower():
                db_instances.append(each_db["DBInstanceIdentifier"])

        return db_instances
    
    def get_rds_host(self, db_instance_id: str) -> str:
        db_instance_info = self.client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
        return db_instance_info["DBInstances"][0]["Endpoint"]["Address"]

    def start_dbs(self, state: str) -> List[str]:
        db_instance_ids: List[str] = self.get_db_ids(state=state)
        for db_instance_id in db_instance_ids:
            self.client.start_db_instance(DBInstanceIdentifier=db_instance_id)
            logger.info(f"Started RDS instance: {db_instance_id}")
        return db_instance_ids

    def stop_rds(self, state: str) -> List[str]:
        db_instance_ids: List[str] = self.get_db_ids(state=state)
        for db_instance_id in db_instance_ids:
            self.client.stop_db_instance(DBInstanceIdentifier=db_instance_id)
            logger.info(f"Stopped RDS instance: {db_instance_id}")
        return db_instance_ids
