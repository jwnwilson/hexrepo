
import os
from typing import List

import typer

AWS_ENV_VARS = [
    "AWS_ACCOUNT",
    "AWS_DEFAULT_REGION",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
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
    shell_command: str = f"echo 'export {env}={value}' >> {shell_file}"
    os.system(shell_command)
    # Update env var for follow up commands
    os.putenv(env, value)
    os.environ[env] = value