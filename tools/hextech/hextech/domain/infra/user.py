import typer
from hextech.config import HexrepoConfig
from hextech.domain.system import run_system_command
from hextech.domain.infra.bastion import managed_bastion_ssh
from hextech.domain.infra.deployment import get_terrform_output


def create_user_with_permissions(config: HexrepoConfig, env: str) -> None:
    project: str = "common"
    if config.cloud_provider == "aws" and env != "local":
        # Start bastion
        with managed_bastion_ssh(config, env, project):
            run_system_command(
                f"cd projects/{project} && make --no-print-directory create_user ENVIRONMENT={env}"
            )
                
    elif env == "local":
        typer.echo("Running migration locally")
        run_system_command(
            f"cd projects/{project} && make --no-print-directory create_user ENVIRONMENT={env}"
        )


def create_user_permissions(config: HexrepoConfig, env: str) -> None:
    project: str = "common"
    if config.cloud_provider == "aws" and env != "local":
        # Start bastion
        with managed_bastion_ssh(config, env, project):
            run_system_command(
                f"cd projects/{project} && make --no-print-directory create_permissions ENVIRONMENT={env}"
            )
                
    elif env == "local":
        typer.echo("Running migration locally")
        run_system_command(
            f"cd projects/{project} && make --no-print-directory create_permissions ENVIRONMENT={env}"
        )