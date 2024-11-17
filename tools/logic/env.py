
import os
from os.path import expanduser
from typing import List
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

import typer


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


def set_env_var(shell_file: str, env: str, value: str):
    typer.echo(f"Saving {env} in {shell_file}")
    env_command: str = f'export {env}="{value}"\n'
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
