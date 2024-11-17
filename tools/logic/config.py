
import json
from typing import List, Optional, Tuple, Union
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import typer

from tools.logic.env import set_env_var
from tools.prompts.common import prompt_cloud_provider, prompt_shell_file
from tools.prompts.config import prompt_config_setup, prompt_environments
from tools.prompts.infra import prompt_aws_config
from tools.templates.libs import generate_libs_makefile


class AWSConfig(BaseModel):
    AWS_ACCOUNT: str
    AWS_DEFAULT_REGION: str
    AWS_TF_STATE_BUCKET: str


class MonorepoConfig(BaseSettings):
    project_name: str = "monorepo"
    shell_file: str = "~/.zshrc"
    cloud_provider: str = "aws"
    cloud_provider_config: Union[AWSConfig] = {}
    environments: List[str] = ["dev", "prd"]
    monorepo_lib_repo_url: str = ""
    monorepo_lib_repo_username: str = ""

    def set_config_var(self, key: str, value: str, set_env_var: bool = False):
        setattr(self, key, value)
        self.save_config()
        if set_env_var:
            set_env_var(self.shell_file, key.upper(), value)

    def save_config(self):
        with open("config.json", "w") as f:
            f.write(self.model_dump_json())

    def set_env_var(self, key: str, value: str):
        set_env_var(self.shell_file, key, value)

    @classmethod
    def load_config() -> Optional["MonorepoConfig"]:
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
    if cloud_provider == "aws":
        cloud_config: AWSConfig = prompt_aws_config()

    config: MonorepoConfig = MonorepoConfig(
        shell_file=shell_file,
        cloud_provider=cloud_provider,
        cloud_provider_config=cloud_config,
        environments=environments,
    )

    with open("config.json", "w") as f:
        f.write(config.model_dump_json())

    return config


def get_or_create_config() -> Tuple[MonorepoConfig, bool]:
    created_config: bool = False
    config: Optional[MonorepoConfig] = MonorepoConfig.load_config()
    if not config or prompt_config_setup():
        config: MonorepoConfig = setup_project_config()
        created_config = True
    if not config: 
        typer.echo("Unable to load config file, aborting.")
        raise typer.Abort()
    return (config, created_config)
