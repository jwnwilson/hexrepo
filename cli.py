import os
from contextlib import chdir
from typing import List, Optional
from cookiecutter.main import cookiecutter
import typer

from tools.logic.config import MonorepoConfig, get_or_create_config
from tools.logic.infra import authenticate_cloud, create_lib_infra, create_tf_state, deploy_projects, publish_libs, run_system_command, setup_global_env_infra
from tools.logic.project import get_libraries, get_library_type, get_projects, install_library_in_project
from tools.prompts.common import prompt_library_type
from tools.prompts.infra import prompt_deploy_libs, prompt_setup_lib_infra, prompt_setup_project_infra, prompt_setup_shared_infra, prompt_setup_tf
from tools.templates.libs import generate_libs_makefile

app = typer.Typer()


@app.command()
def create_be_library():
    library_type = prompt_library_type()
    # CD to libs/src/adaptor or libs/src/interactor folder
    with chdir(f"libs/src/{library_type}"):
        # Run cookie cutter command to copy template
        cookiecutter("../../../templates/library")
        # Setup infra for libray
        if prompt_setup_lib_infra():
            typer.echo("Setting up library infrastructure...")
            os.system("make tf_init")
            os.system("make tf_plan")
            os.system("make tf_apply")
            typer.echo("Shared infrastructure setup complete.")


@app.command()
def create_be_project():
    # CD to projects folder
    with chdir(f"projects"):
        # Run cookie cutter command to copy template
        cookiecutter("../templates/project")
        # Setup infra for service
        if prompt_setup_project_infra():
            typer.echo("Setting up project infrastructure...")
            os.system("make tf_init")
            os.system("make tf_plan")
            os.system("make tf_apply")
            typer.echo("Shared infrastructure setup complete.")


@app.command()
def add_be_library(project: str, library: str):
    # Install library from repo if available
    install_library_in_project(library, project)


@app.command()
def setup():
    # project config setup
    config: MonorepoConfig
    created_config: bool
    config, created_config = get_or_create_config()

    # Copy libs makefile to libs
    if created_config:
        generate_libs_makefile(config)

    # Create initial terraform state infra
    if prompt_setup_tf():
        create_tf_state(config)

    # Add options to deploy repo to cloud provider
    if prompt_setup_lib_infra():
        create_lib_infra(config)
    
    authenticate_cloud(config)

    # Publish libraries to repo
    if prompt_deploy_libs():
        publish_libs(config)

    # Setup shared infra for environments
    if prompt_setup_shared_infra():
        setup_global_env_infra(config)


@app.command()
def test_be_projects(run_all: bool = True):
    if run_all:
        projects: List[str] = get_projects()
    else:
        # get list of modified files
        # find projects that have been modified
        # run tests for those projects
        raise NotImplementedError("Not implemented yet")
    for project in projects:
        typer.echo(f"Running linting check for {project}...")
        run_system_command(f"cd projects/{project} && make lint_check")
        typer.echo(f"Running tests check for {project}...")
        run_system_command(f"cd projects/{project} && make test")


@app.command()
def test_be_libs(libraries: Optional[List[str]] = None):
    repo_libs: List[str] = get_libraries()
    libraries = libraries.remove("") if "" in libraries else libraries

    if not libraries:
        libraries: List[str] = get_libraries()
    else:
        assert all(lib in repo_libs for lib in libraries), "Invalid library name provided"
    
    for lib in libraries:
        lib_type: str = get_library_type(lib)
        typer.echo(f"Running linting check for {lib}...")
        run_system_command(f"cd libs/src/{lib_type}/{lib} && make lint_check")
        typer.echo(f"Running tests check for {lib}...")
        run_system_command(f"cd libs/src/{lib_type}/{lib} && make test")


@app.command()
def deploy_be_libs(libraries: Optional[List[str]] = None, check_modified: bool = False, no_input: bool = False):
    config: MonorepoConfig
    config, _ = get_or_create_config(no_input=no_input)
    libraries = libraries.remove("") if "" in libraries else libraries

    publish_libs(config, libraries=libraries, check_modified=check_modified)


@app.command()
def deploy_be_projects(projects: Optional[List[str]] = None, check_modified: bool = False, no_input: bool = False):
    config: MonorepoConfig
    config, _ = get_or_create_config(no_input=no_input)
    projects = projects.remove("") if "" in projects else projects

    deploy_projects(config, projects=projects, check_modified=check_modified)



if __name__ == "__main__":
    app()