from typing import List, Optional
import boto3
import logging

import typer

from tools.logic.config import MonorepoConfig

logger = logging.getLogger()    


def start_infra_command(config: MonorepoConfig):
    region: str = config.cloud_provider_config.AWS_DEFAULT_REGION
    # start bastion instances that are not running
    start_ec2s(region)
    # start rds instances that are not running
    start_rds(region)
    

def stop_infra_command(config: MonorepoConfig):
    region: str = config.cloud_provider_config.AWS_DEFAULT_REGION
    # start bastion instances that are not running
    stop_ec2s(region)
    # start rds instances that are not running
    stop_rds(region)


def _get_ec2_instances(ec2, state: Optional[str] = None) -> List[str]:
    instance_data = ec2.describe_instances()
    instancelist = []
    for reservation in instance_data["Reservations"]:
        for instance in reservation["Instances"]:
            if not state:
                instancelist.append(instance["InstanceId"])
            elif instance["State"]['Name'].lower() == state.lower():
                instancelist.append(instance["InstanceId"])
    return instancelist


def start_ec2s(region: str):
    # start bastion instances that are not running
    ec2 = boto3.client('ec2', region_name=region)
    ec2_ids = _get_ec2_instances(ec2, state='stopped')

    if ec2_ids:
        ec2.start_instances(InstanceIds=ec2_ids)
        for i in ec2_ids:
            typer.echo('Started your instances: ' + str(i))


def stop_ec2s(region: str):
    ec2 = boto3.client('ec2', region_name=region)
    ec2_ids = _get_ec2_instances(ec2, state='running')

    if ec2_ids:
        ec2.stop_instances(InstanceIds=ec2_ids)
        for i in ec2_ids:
            typer.echo('Started your instances: ' + str(i))


def _get_rds_ids(region: str, state: Optional[str] = None) -> List[str]:
    rds_client = boto3.client('rds', region)
    db_instance_info = rds_client.describe_db_instances()

    db_instances = []
    for each_db in db_instance_info['DBInstances']: 
        if not state:
            db_instances.append(each_db['DBInstanceIdentifier'])
        elif each_db['DBInstanceStatus'].lower() == state.lower():
            db_instances.append(each_db['DBInstanceIdentifier'])

    return db_instances


def start_rds(region: str):
    # start rds instances that are not running
    rds_client = boto3.client('rds', region)
    db_instance_ids = _get_rds_ids(region, state='stopped')
    for db_instance_id in db_instance_ids:
        rds_client.start_db_instance(DBInstanceIdentifier=db_instance_id)
        typer.echo(f"Started RDS instance: {db_instance_id}")


def stop_rds(region: str):
    # stop rds instances that are running
    rds_client = boto3.client('rds', region)
    db_instance_ids = _get_rds_ids(region, state='available')
    for db_instance_id in db_instance_ids:
        rds_client.stop_db_instance(DBInstanceIdentifier=db_instance_id)
        typer.echo(f"Stopped RDS instance: {db_instance_id}")
