import typer

from tools.logic.config import AWSConfig, MonorepoConfig
from tools.logic.env import set_env_var


def prompt_setup_tf() -> bool:
    return typer.confirm("Would you like to setup Terraform state?")


def prompt_setup_lib_infra() -> bool:
    return typer.confirm("Would you like to setup infrastructure for libraries?")


def prompt_setup_shared_infra() -> bool:
    return typer.confirm("Would you like to setup shared infrastructure for environments?")


def prompt_setup_project_infra() -> bool:
    return typer.confirm("Would you like to setup infrastructure for the project?")


def prompt_deploy_libs() -> bool:
    return typer.confirm("Would you like to deploy libraries?")


def prompt_aws_config(config: MonorepoConfig) -> AWSConfig:
    aws_config: AWSConfig = AWSConfig(
        AWS_ACCOUNT=typer.prompt("Please enter your AWS account ID:"),
        AWS_DEFAULT_REGION=typer.prompt("Please enter your AWS default region: [us-east-1, eu-west-1, etc]", default="eu-west-1"),
        AWS_TF_STATE_BUCKET=typer.prompt("Please enter your AWS Terraform state bucket name:", default="monorepo")
    )   

    access_key_id: str = typer.prompt("Please enter your AWS monorepo user access key id:"),
    access_secret_key: str = typer.prompt("Please enter your AWS monorepo user secret access key:")
    
    set_env_var(config.shell_file, "AWS_ACCESS_KEY_ID", access_key_id)
    set_env_var(config.shell_file, "AWS_SECRET_ACCESS_KEY", access_secret_key)
    set_env_var(config.shell_file, "AWS_ACCOUNT", aws_config.AWS_ACCOUNT)
    set_env_var(config.shell_file, "AWS_DEFAULT_REGION", aws_config.AWS_DEFAULT_REGION)
    
    return aws_config 