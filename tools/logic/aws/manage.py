from typing import List, Optional
import boto3
import logging

logger = logging.getLogger()    


def start_infra(region: str):
    # start bastion instances that are not running
    start_bastions(region)
    # start rds instances that are not running
    start_rds(region)
    

def stop_infra(region: str):
    # start bastion instances that are not running
    stop_bastions(region)
    # start rds instances that are not running
    stop_rds(region)


def _get_bastion_ids(ec2, state: Optional[str] = None) -> List[str]:
    instance_iterator = ec2.instances.filter(
        Filters=[
            {
                'Name': 'Type',
                'Values': ['bastion']
            }
    ])

    instancelist = []
    for instance in instance_iterator:
        if not state:
            instancelist.append(instance["InstanceId"])
        elif instance["State"]['Name'] == state:
            instancelist.append(instance["InstanceId"])
    return instancelist


def start_bastions(region: str):
    # start bastion instances that are not running
    ec2 = boto3.client('ec2', region_name=region)
    bastions_ids = _get_bastion_ids(ec2, state='stopped')

    if bastions_ids:
        ec2.stop_instances(InstanceIds=bastions_ids)
        for i in bastions_ids:
            logger.info('Stopped your instances: ' + str(i))


def stop_bastions(region: str):
    ec2 = boto3.client('ec2', region_name=region)
    bastions_ids = _get_bastion_ids(ec2, state='running')

    if bastions_ids:
        ec2.start_instances(InstanceIds=bastions_ids)
        for i in bastions_ids:
            logger.info('Started your instances: ' + str(i))


def _get_rds_ids(region: str, state: Optional[str] = None) -> List[str]:
    rds_client = boto3.client('rds', region)
    db_instance_info = rds_client.describe_db_instances()

    db_instances = []
    for each_db in db_instance_info['DBInstances']: 
        if each_db['DBInstanceStatus'] == state:
            db_instances.append(each_db['DBInstanceIdentifier'])

    return [each_db['DBInstanceIdentifier'] for each_db in db_instances]


def start_rds(region: str):
    # start rds instances that are not running
    rds_client = boto3.client('rds', region)
    db_instance_ids = _get_rds_ids(region, state='stopped')
    rds_client.start_db_instance(DBInstanceIdentifier=db_instance_ids)


def stop_rds(region: str):
    # stop rds instances that are running
    rds_client = boto3.client('rds', region)
    db_instance_ids = _get_rds_ids(region, state='available')
    rds_client.stop_db_instance(DBInstanceIdentifier=db_instance_ids)

