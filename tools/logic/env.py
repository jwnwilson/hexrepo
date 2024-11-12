
import os
from os.path import expanduser
from typing import List
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

import typer

from tools.prompts.common import prompt_shell_file

AWS_ENV_VARS = [
    "AWS_ACCOUNT",
    "AWS_DEFAULT_REGION",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_TF_STATE_BUCKET"
]


def value_in_file(file_path: str, value: str) -> bool:
    abs_file_path: str = expanduser(file_path)
    with open(abs_file_path) as f:
        if value in f.read():
            return True
        else:
            return False
    

def replace(file_path: str, pattern: str, subst: str):
    #Create temp file
    fh, temp_path = mkstemp()
    file_path: str = expanduser(file_path)
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                if pattern in line:
                    new_file.write(subst)
                else:
                    new_file.write(line)
    #Copy the file permissions from the old file to the new file
    copymode(file_path, temp_path)
    #Remove original file
    remove(file_path)
    #Move new file
    move(temp_path, file_path)


def check_missing_env_vars(cloud_provider: str) -> List[str]:
    missing_envs = []
    if cloud_provider == "aws":
        for env in AWS_ENV_VARS:
            if env not in os.environ:
                missing_envs.append(env)
        
    return missing_envs


def set_env_var(shell_file: str, env: str, value: str):
    typer.echo(f"Saving {env} in {shell_file}")
    env_command: str = f'export {env}="{value}"'
    # Replace existing value if it exists
    if value_in_file(shell_file, env):
        replace(shell_file, env, env_command)
    else:
        # Else append to file
        shell_command: str = f"echo '{env_command}' >> {shell_file}"
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
