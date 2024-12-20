
import json
from typing import List, Optional, Tuple, Union
from pydantic_settings import BaseSettings
import typer

from monorepo_cloud.config import AWSConfig
from hextech.domain.system import set_env_var
from hextech.domain.prompts.common import prompt_cloud_provider, prompt_shell_file
from hextech.domain.prompts.config import prompt_config_setup, prompt_environments


class MonorepoConfig(BaseSettings):
    project_name: str = "monorepo"
    shell_file: str = "~/.zshrc"
    cloud_provider: str = "aws"
    cloud_provider_config: Optional[Union[AWSConfig]] = None
    environments: List[str] = ["dev", "prd"]
    monorepo_lib_repo_url: str = ""
    monorepo_lib_repo_username: str = ""

    def set_config_var(self, key: str, value: str, set_env: bool = False):
        setattr(self, key, value)
        self.save_config()
        if set_env:
            set_env_var(self.shell_file, key.upper(), value)

    def save_config(self):
        with open("config.json", "w") as f:
            f.write(self.model_dump_json(indent=4))

    def set_env_var(self, key: str, value: str):
        set_env_var(self.shell_file, key, value)

    @classmethod
    def load_config(cls) -> Optional["MonorepoConfig"]:
        try:
            with open("config.json", "r") as f:
                config = json.loads(f.read())
            return MonorepoConfig(**config)
        except Exception as err:
            print("Unable to load config file.")
            return None
        

def aws_config(config: MonorepoConfig) -> MonorepoConfig:
    aws_config: AWSConfig = AWSConfig(
        AWS_ACCOUNT=typer.prompt("Please enter your AWS account ID"),
        AWS_REGION=typer.prompt("Please enter your AWS region", default="eu-west-1"),
        AWS_TF_STATE_BUCKET=typer.prompt("Please enter your AWS Terraform state bucket name", default="monorepo")
    )   

    access_key_id: str = typer.prompt("Please enter your AWS monorepo user access key id")
    access_secret_key: str = typer.prompt("Please enter your AWS monorepo user secret access key")
    
    set_env_var(config.shell_file, "AWS_ACCESS_KEY_ID", access_key_id)
    set_env_var(config.shell_file, "AWS_SECRET_ACCESS_KEY", access_secret_key)
    set_env_var(config.shell_file, "AWS_ACCOUNT", aws_config.AWS_ACCOUNT)
    set_env_var(config.shell_file, "AWS_DEFAULT_REGION", aws_config.AWS_REGION)
    
    config.cloud_provider_config = aws_config

    return config 


def setup_project_config() -> MonorepoConfig:
    shell_file = prompt_shell_file()
    cloud_provider = prompt_cloud_provider()
    environments = prompt_environments()

    config: MonorepoConfig = MonorepoConfig(
        shell_file=shell_file,
        cloud_provider=cloud_provider,
        environments=environments,
    )

    if cloud_provider == "aws":
        config: MonorepoConfig = aws_config(config)
    
    with open("config.json", "w") as f:
        f.write(config.model_dump_json())

    return config


def get_or_create_config(no_input: bool = False) -> Tuple[MonorepoConfig, bool]:
    created_config: bool = False
    config: Optional[MonorepoConfig] = MonorepoConfig.load_config()
    if not config or (not no_input and prompt_config_setup()):
        config: MonorepoConfig = setup_project_config()
        created_config = True
    if not config: 
        typer.echo("Unable to load config file, aborting.")
        raise typer.Abort()
    return (config, created_config)


