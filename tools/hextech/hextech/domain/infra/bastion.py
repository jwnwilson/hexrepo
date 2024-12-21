import os
import signal
import subprocess
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import typer
from monorepo_cloud.compute import AWSComputeManager
from monorepo_cloud.db import AWSRDSManager

from hextech.config import MonorepoConfig

from ..system import run_system_command


def bastion_ssh_tunnel(
    config: MonorepoConfig, env: str, project: str, background_task: bool = False
) -> Optional[Any]:
    if config.cloud_provider == "aws":
        compute_manager: AWSComputeManager = AWSComputeManager(
            config.cloud_provider_config
        )
        rds_manageer: AWSRDSManager = AWSRDSManager(config.cloud_provider_config)
        instance_ids: List[str] = compute_manager.get_instances_ids(
            tags={"Type": "bastion", "Environment": env}
        )
        rds_host: str = rds_manageer.get_rds_host(
            tags={"Project": project, "Environment": env}
        )

        if not instance_ids:
            raise typer.Abort("No bastion instance found")
        if len(instance_ids) > 1:
            raise typer.Abort("Multiple bastion instances found")

        bastion_command: str = f"""
            aws ssm start-session \
            --target {instance_ids[0]} \
            --document-name AWS-StartPortForwardingSessionToRemoteHost \
            --parameters '{{"portNumber":["5432"],"localPortNumber":["5432"], "host":["{rds_host}"]}}'
        """
        if background_task:
            return subprocess.Popen(bastion_command, shell=True, preexec_fn=os.setsid)
        else:
            run_system_command(bastion_command)


@contextmanager
def managed_bastion_ssh(config: MonorepoConfig, env: str, project: str):
    typer.echo(f"Starting ssh tunnel to bastion")
    bastion_process = bastion_ssh_tunnel(config, env, project, background_task=True)
    try:
        yield bastion_process
    finally:
        typer.echo(f"Shutting down ssh tunnel to bastion")
        os.killpg(os.getpgid(bastion_process.pid), signal.SIGTERM)
        print("Shut down ssh tunnel to bastion")


def db_exists(
    config: MonorepoConfig,
    project: str,
    env: str,
) -> bool:
    rds_manageer: AWSRDSManager = AWSRDSManager(config.cloud_provider_config)
    try:
        rds_manageer.get_rds_host(tags={"Project": project, "Environment": env})
    except IndexError:
        return False
    return True
