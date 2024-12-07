from pydantic import BaseModel 
import typer

from tools.logic.config import MonorepoConfig
from tools.logic.env import set_env_var


class AWSConfig(BaseModel):
    AWS_ACCOUNT: str
    AWS_DEFAULT_REGION: str
    AWS_TF_STATE_BUCKET: str


def aws_config(config: MonorepoConfig) -> MonorepoConfig:
    aws_config: AWSConfig = AWSConfig(
        AWS_ACCOUNT=typer.prompt("Please enter your AWS account ID"),
        AWS_DEFAULT_REGION=typer.prompt("Please enter your AWS default region", default="eu-west-1"),
        AWS_TF_STATE_BUCKET=typer.prompt("Please enter your AWS Terraform state bucket name", default="monorepo")
    )   

    access_key_id: str = typer.prompt("Please enter your AWS monorepo user access key id")
    access_secret_key: str = typer.prompt("Please enter your AWS monorepo user secret access key")
    
    set_env_var(config.shell_file, "AWS_ACCESS_KEY_ID", access_key_id)
    set_env_var(config.shell_file, "AWS_SECRET_ACCESS_KEY", access_secret_key)
    set_env_var(config.shell_file, "AWS_ACCOUNT", aws_config.AWS_ACCOUNT)
    set_env_var(config.shell_file, "AWS_DEFAULT_REGION", aws_config.AWS_DEFAULT_REGION)
    
    config.cloud_provider_config = aws_config

    return config 
