
import json
import os
import signal
import subprocess
from typing import Any, Dict, List, Optional

import typer
from hexcli.config import MonorepoConfig
from monorepo_cloud.compute import AWSComputeManager
from monorepo_cloud.db import AWSRDSManager
from ..system import run_system_command


def bastion_ssh_tunnel(config: MonorepoConfig, env: str, project: str, background_task: bool = False) -> Optional[Any]:
    if config.cloud_provider == "aws":
        compute_manager: AWSComputeManager = AWSComputeManager(config.cloud_provider_config)
        rds_manageer: AWSRDSManager = AWSRDSManager(config.cloud_provider_config)
        instance_ids: List[str] = compute_manager.get_instances(
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

