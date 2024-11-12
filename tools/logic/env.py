
import os
from typing import List

import typer

from tools.prompts.common import prompt_shell_file

AWS_ENV_VARS = [
    "AWS_ACCOUNT",
    "AWS_DEFAULT_REGION",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_TF_STATE_BUCKET"
]


def check_missing_env_vars(cloud_provider: str) -> List[str]:
    missing_envs = []
    if cloud_provider == "aws":
        for env in AWS_ENV_VARS:
            if env not in os.environ:
                missing_envs.append(env)
        
    return missing_envs


def set_env_var(shell_file: str, env: str, value: str):
    typer.echo(f"Saving {env} in {shell_file}")
    # Replace existing value if it exists
    # Else append to file
    shell_command: str = f"echo 'export {env}={value}' >> {shell_file}"
    os.system(shell_command)
    # Update env var for follow up commands
    os.putenv(env, value)
    os.environ[env] = value


def setup_env_vars(shell_file: str, cloud_provider: str):
    missing_envs: List[str] = check_missing_env_vars(cloud_provider)
    
    if not missing_envs:
        return
    
    new_env_vars = {}
    for env in missing_envs:
        new_env_vars[env] = typer.prompt(f"Env value: {env} not found, please enter {env}")

    for env in new_env_vars:
        set_env_var(shell_file, env, new_env_vars[env])
