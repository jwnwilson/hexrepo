
import subprocess
from typing import Any, List, Optional

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
            return subprocess.Popen(bastion_command.split(" "))
        else:
            run_system_command(bastion_command)


def get_terrform_output(env: str, project: str) -> str:
    return run_system_command(f"cd projects/{project} && make tf_oputput ENV={env}")


def migrate_db(config: MonorepoConfig, env: str, project: str):
    if config.cloud_provider == "aws":
        # Start bastion
        bastion_process = bastion_ssh_tunnel(config, env, project, background_task=True)

        # Get secret name
        secret_name = "db"
        # terraform_output: Dict = get_terrform_output(env, project)
        # secret_name = terraform_output["db_password_secret_name"]

        # Run migration with secret name set
        run_system_command(f"cd projects/{project} && make db_migrate DB_PASSWORD_SECRET_NAME={secret_name}")

        # Terminate bastiob
        bastion_process.terminate()
