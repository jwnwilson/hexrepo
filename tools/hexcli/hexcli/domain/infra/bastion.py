
import json
import subprocess
from typing import Any, Dict, List, Optional

import typer
from hexcli.config import MonorepoConfig
from monorepo_cloud.compute import AWSComputeManager
from monorepo_cloud.db import AWSRDSManager
from ..system import run_system_command, run_system_command_with_output


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
            return subprocess.Popen(bastion_command, shell=True)
        else:
            run_system_command(bastion_command)


def get_terrform_output(env: str, project: str) -> str:
    tf_str: str = run_system_command_with_output(f"cd projects/{project} && make tf_output ENVIRONMENT={env}")
    try:
        return json.loads(tf_str)
    except json.JSONDecodeError as err:
        raise typer.Abort(f"Error parsing terraform output: {err}")


def migrate_db(config: MonorepoConfig, env: str, project: str):
    if config.cloud_provider == "aws":
        # Start bastion
        bastion_process = bastion_ssh_tunnel(config, env, project, background_task=True)
        try:
            # Get secret name
            secret_name: str = ""
            db_url: str = ""
            if env != "local":
                tf_output: Dict[str, str] = get_terrform_output(env, project)
                secret_name = tf_output["db_secret_name"]["value"]
                db_url = "postgresql+psycopg2://postgres:{password}@localhost:5432/" + project

            # Run migration with secret name set
            # stop making docker db call
            run_system_command(f"cd projects/{project} && make db_upgrade DB_PASSWORD_SECRET_NAME={secret_name} DB_URL={db_url} CLOUD_PROVIDER={config.cloud_provider}")
        finally:
            # Terminate bastion
            bastion_process.terminate()
