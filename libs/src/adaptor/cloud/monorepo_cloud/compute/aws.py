

from typing import List, Optional
import logging
import boto3
from monorepo_cloud.config import AWSConfig

logger = logging.getLogger()


class AWSComputeManager():
    def __init__(self, config: AWSConfig):
        self.config: AWSConfig = config
        self.ec2 = boto3.client('ec2', region_name=self.aws_config.AWS_DEFAULT_REGION)

    def get_instances(self, state: Optional[str] = None) -> List[str]:
        instance_data = self.ec2.describe_instances()
        instancelist = []
        for reservation in instance_data["Reservations"]:
            for instance in reservation["Instances"]:
                if not state:
                    instancelist.append(instance["InstanceId"])
                elif instance["State"]['Name'].lower() == state.lower():
                    instancelist.append(instance["InstanceId"])
        return instancelist
    
    def start_instances(self, state: Optional[str] = None) -> List[str]:
        # start bastion instances that are not running
        instance_ids: List[str] = self.get_instances(state=state)

        if instance_ids:
            self.ec2.start_instances(InstanceIds=instance_ids)

        logger.info('Started instances: ' + str(instance_ids))
        
        return instance_ids
    
    def stop_instances(self, state: Optional[str] = None) -> List[str]:
        # start bastion instances that are not running
        instance_ids: List[str] = self.get_instances(state=state)

        if instance_ids:
            self.ec2.stop_instances(InstanceIds=instance_ids)

        logger.info('Stopped instances: ' + str(instance_ids))
        
        return instance_ids
