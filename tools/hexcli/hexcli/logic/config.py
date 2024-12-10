
import json
from typing import List, Optional, Tuple, Union
from pydantic_settings import BaseSettings
import typer

from hexcli.logic.aws.config import AWSConfig, aws_config
from hexcli.logic.env import set_env_var
from hexcli.prompts.common import prompt_cloud_provider, prompt_shell_file
from hexcli.prompts.config import prompt_config_setup, prompt_environments


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


