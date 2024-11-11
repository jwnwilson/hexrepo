import os
from typing import List
from cookiecutter.main import cookiecutter
import typer

from tools.logic.folder import get_projects, get_libraries, get_library_type
from tools.logic.env import check_missing_env_vars, set_env_var
from tools.prompts.common import prompt_cloud_provider, prompt_library_type, prompt_shell_file
from tools.templates.libs import generate_libs_makefile

app = typer.Typer()


@app.command()
def create_be_library():
    library_type = prompt_library_type()
    # CD to libs/src/adaptor or libs/src/interactor folder
    os.chdir(f"backend/libs/src/{library_type}")
    # Run cookie cutter command to copy template
    cookiecutter("../../../templates/library")


@app.command()
def create_be_project():
    # CD to projects folder
    os.chdir(f"backend/projects")
    # Run cookie cutter command to copy template
    cookiecutter("../templates/project")


@app.command()
def add_be_library(project: str, library: str):
    # Install library locally in poetry dev group
    libraries: List[str] = get_libraries()
    projects: List[str] = get_projects()

    assert project in projects, f"Project {project} not found"
    assert library in libraries, f"Library {library} not found"

    # Install library from repo if available
    library_type = get_library_type(library)
    os.chdir(f"backend/projects/{project}") 
    os.system(f"poetry add --editable ../../libs/src/{library_type}/{library} -G dev")
    os.system(f"poetry add {library} -G prod")


@app.command()
def setup():
    cloud_provider: str = prompt_cloud_provider()
    # Check if env vars exist
    missing_envs: List[str] = check_missing_env_vars(cloud_provider)
    new_env_vars = {}
    for env in missing_envs:
        new_env_vars[env] = typer.prompt(f"Env value: {env} not found, please enter {env}")

    # Pick ~/.bashrc or ~/.zshrc based on shell
    shell_file: str = prompt_shell_file()

    # Save env vars in ~/.bashrc or ~/.zshrc
    for env in new_env_vars:
        set_env_var(shell_file, env, new_env_vars[env])

    # Copy libs makefile to libs
    generate_libs_makefile(cloud_provider)

    # Add options to deploy repo to cloud provider


if __name__ == "__main__":
    app()