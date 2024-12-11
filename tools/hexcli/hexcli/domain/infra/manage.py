from typing import List, Optional
import boto3
import logging

import typer

from monorepo_cloud.compute import AWSComputeManager
from monorepo_cloud.db import AWSRDSManager
from tools.hexcli.hexcli.config import MonorepoConfig

logger = logging.getLogger()    


def start_infra_command(config: MonorepoConfig):
    if config.cloud_provider == "aws":
        aws_compute_manager = AWSComputeManager(config.cloud_provider_config)
        aws_rds_manager = AWSRDSManager(config.cloud_provider_config)
        # start bastion instances that are not running
        started_instances: List[str] = aws_compute_manager.start_instance(state='stopped')
        typer.echo(f"Started instances: {started_instances}")

        # start rds instances that are not running
        started_dbs: List[str] = aws_rds_manager.start_rds(state='stopped')
        typer.echo(f"Started dbs: {started_dbs}")
    

def stop_infra_command(config: MonorepoConfig):
    if config.cloud_provider == "aws":
        aws_compute_manager = AWSComputeManager(config.cloud_provider_config)
        aws_rds_manager = AWSRDSManager(config.cloud_provider_config)
        # start bastion instances that are not running
        stopped_instances: List[str] = aws_compute_manager.stop_instance(state='stopped')
        typer.echo(f"Stopped instances: {stopped_instances}")

        # start rds instances that are not running
        stopped_dbs: List[str] = aws_rds_manager.stop_rds(state='stopped')
        typer.echo(f"Stopped dbs: {stopped_dbs}")
