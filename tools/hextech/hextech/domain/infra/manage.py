import logging
from typing import List, Optional

import boto3
import typer
from monorepo_cloud.compute import AWSComputeManager
from monorepo_cloud.db import AWSRDSManager

from hextech.config import MonorepoConfig

logger = logging.getLogger()


def start_infra_command(config: MonorepoConfig):
    if config.cloud_provider == "aws":
        aws_compute_manager = AWSComputeManager(config.cloud_provider_config)
        aws_rds_manager = AWSRDSManager(config.cloud_provider_config)
        # start bastion instances that are not running
        stopped_instances: List[str] = aws_compute_manager.get_instances_ids(
            state="stopped"
        )
        started_instances: List[str] = aws_compute_manager.start_instances(
            instance_ids=stopped_instances
        )
        typer.echo(f"Started instances: {started_instances}")

        # start rds instances that are not running
        stopped_dbs: List[str] = aws_rds_manager.get_db_ids(state="stopped")
        started_dbs: List[str] = aws_rds_manager.start_dbs(db_instance_ids=stopped_dbs)
        typer.echo(f"Started dbs: {started_dbs}")


def stop_infra_command(config: MonorepoConfig):
    if config.cloud_provider == "aws":
        aws_compute_manager = AWSComputeManager(config.cloud_provider_config)
        aws_rds_manager = AWSRDSManager(config.cloud_provider_config)
        # start bastion instances that are not running
        running_instances: List[str] = aws_compute_manager.get_instances_ids(
            state="running"
        )
        stopped_instances: List[str] = aws_compute_manager.stop_instances(
            instance_ids=running_instances
        )
        typer.echo(f"Stopped instances: {stopped_instances}")

        # start rds instances that are not running
        running_dbs: List[str] = aws_rds_manager.get_db_ids(state="running")
        stopped_dbs: List[str] = aws_rds_manager.stop_rds(db_instance_ids=running_dbs)
        typer.echo(f"Stopped dbs: {stopped_dbs}")
