from typing import List, Optional
import boto3
import logging

import typer

from monorepo_cloud.compute import AWSComputeManager
from hexcli.logic.config import MonorepoConfig

logger = logging.getLogger()    


def start_infra_command(config: MonorepoConfig):
    aws_compute_manager = AWSComputeManager(config.cloud_provider_config)
    aws_rds_manager = AWSRDSManager(config.cloud_provider_config)
    # start bastion instances that are not running
    aws_compute_manager.start_instance(state='stopped')
    # start rds instances that are not running
    aws_rds_manager.start_rds(state='stopped')
    

def stop_infra_command(config: MonorepoConfig):
    aws_compute_manager = AWSComputeManager(config.cloud_provider_config)
    aws_rds_manager = AWSRDSManager(config.cloud_provider_config)
    # start bastion instances that are not running
    aws_compute_manager.stop_instance(state='stopped')
    # start rds instances that are not running
    aws_rds_manager.stop_rds(state='stopped')


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
