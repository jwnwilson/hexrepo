import os
from typing import List
from cookiecutter.main import cookiecutter
import typer

from tools.logic.infra import create_lib_infra, create_tf_state, publish_libs
from tools.logic.project import get_projects, get_libraries, get_library_type, install_library_in_project
from tools.logic.env import check_missing_env_vars, set_env_var, setup_env_vars
from tools.prompts.common import prompt_cloud_provider, prompt_library_type, prompt_shell_file
from tools.prompts.infra import prompt_deploy_libs, prompt_setup_lib_infra, prompt_setup_tf
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
    # Install library from repo if available
    install_library_in_project(library, project)


@app.command()
def setup():
    cloud_provider: str = prompt_cloud_provider()
    
    # Setup cloud provider env vars
    setup_env_vars(cloud_provider)

    # Copy libs makefile to libs
    generate_libs_makefile(cloud_provider)

    # Create initial terraform state infra
    if prompt_setup_tf():
        create_tf_state(cloud_provider)

    # Add options to deploy repo to cloud provider
    if prompt_setup_lib_infra():
        create_lib_infra()

    # Publish libraries to repo
    if prompt_deploy_libs():
        publish_libs()



if __name__ == "__main__":
    app()