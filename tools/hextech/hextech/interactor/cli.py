import contextlib
import os
from contextlib import chdir
from typing import List, Optional

import typer
from cookiecutter.main import cookiecutter
from typing_extensions import Annotated

from hextech.config import HexrepoConfig, get_or_create_config
from hextech.domain.infra.bastion import bastion_ssh_tunnel
from hextech.domain.infra.deployment import (
    create_env_infra,
    create_shared_infra,
    destroy_env_infra,
    destroy_shared_infra,
    plan_env_infra_command,
    publish_libs,
    shared_infra_apply_command,
    shared_infra_plan_command,
)
from hextech.domain.infra.deployment import deploy_projects as deploy_projects_command
from hextech.domain.infra.deployment import migrate_db as migrate_db_func
from hextech.domain.infra.manage import start_infra_command, stop_infra_command
from hextech.domain.infra.storage import create_tf_state
from hextech.domain.project import (
    get_libraries,
    get_library_type,
    get_modified_libraries,
    get_modified_projects,
    get_projects,
    install_library_in_project,
    library_version_bump_required,
    validate_libraries,
)
from hextech.domain.prompts.common import (
    prompt_environment,
    prompt_library,
    prompt_library_type,
    prompt_project,
)
from hextech.domain.prompts.infra import (
    prompt_destroy,
    prompt_setup_lib_infra,
    prompt_setup_project_infra,
    prompt_setup_shared_infra,
    prompt_setup_tf,
)
from hextech.domain.system import run_system_command
from hextech.domain.templates.libs import (
    generate_libs_makefile,
    generate_project_makefile,
)

app = typer.Typer()


@app.command()
def setup():
    # project config setup
    config: HexrepoConfig
    created_config: bool
    config, created_config = get_or_create_config()

    # Copy libs makefile to libs
    # Move these to cookie cutter pre-gen hooks
    if created_config:
        generate_libs_makefile(config)
    generate_project_makefile(config)

    # Create initial terraform state infra
    if prompt_setup_tf():
        create_tf_state(config)

    # Setup initial infra for all projects
    if prompt_setup_shared_infra():
        create_shared_infra(config)
        for env in config.environments:
            create_env_infra(config, env)


@app.command()
def destroy():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    if prompt_destroy():
        for project in get_projects():
            run_system_command(f"cd projects/{project} && make tf_destroy")
        for env in config.environments:
            destroy_env_infra(config, env)
        destroy_shared_infra(config)


@app.command()
def create_library():
    library_type = prompt_library_type()
    # CD to libs/adaptor or libs/interactor folder
    with chdir(f"libs/{library_type}"):
        # Run cookie cutter command to copy template
        cookiecutter("../../templates/library")
        # Setup infra for libray
        if prompt_setup_lib_infra():
            typer.echo("Setting up library infrastructure...")
            run_system_command("make tf_init")
            run_system_command("make tf_plan")
            run_system_command("make tf_apply")
            typer.echo("Shared infrastructure setup complete.")


@app.command()
def create_project():
    # rm template .venv folder to speed up cookectter
    os.system("rm -r templates/project/.venv 2> /dev/null || echo > /dev/null")
    # CD to projects folder
    with chdir("projects"):
        # Run cookie cutter command to copy template
        cookiecutter("../templates/project")
        # Setup infra for service
        if prompt_setup_project_infra():
            typer.echo("Setting up initial infrastructure...")
            run_system_command("make tf_setup ENVIROMENT=default")
            typer.echo("Initial infrastructure setup complete.")


@app.command()
def add_library():
    library: str = prompt_library()
    project: str = prompt_project()
    # Install library from repo if available
    install_library_in_project(library, project)


@app.command()
def shared_infra_plan():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    shared_infra_plan_command(config)


@app.command()
def shared_infra_apply():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    shared_infra_apply_command(config, no_input=True)


@app.command()
def env_infra_plan(env: str):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    plan_env_infra_command(config, env)


@app.command()
def env_infra_apply(env: str):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    create_env_infra(config, env, no_input=True)


@app.command()
def test_projects(run_all: bool = True):
    if run_all:
        projects: List[str] = get_projects()
    else:
        # get list of modified files
        # find projects that have been modified
        # run tests for those projects
        raise NotImplementedError("Not implemented yet")
    for project in projects:
        typer.echo(f"Running linting for {project} project...")
        run_system_command(f"cd projects/{project} && make lint_check")
        typer.echo(f"Running tests for {project} project...")
        run_system_command(f"cd projects/{project} && make test")


@app.command()
def test_libs(libraries: Optional[List[str]] = None):
    libraries: List[str] = validate_libraries(libraries)

    for lib in libraries:
        lib_type: str = get_library_type(lib)
        typer.echo(f"Running linting for {lib} library...")
        run_system_command(f"cd libs/{lib_type}/{lib} && make lint_check")
        typer.echo(f"Running tests for {lib} library...")
        run_system_command(f"cd libs/{lib_type}/{lib} && make test")


@app.command()
def test_tools():
    typer.echo("Running tests for hextech...")
    run_system_command("cd tools/hextech && make test")


@app.command()
def check_library_bump(lib: str):
    libraries: List[str] = validate_libraries(libraries)
    assert lib in libraries, "Invalid library name provided"
    if library_version_bump_required(lib):
        typer.echo(f"Library: '{lib}' needs version bump")
        raise typer.Abort(
            f"library '{lib}' needs version bump, (please commit version bump)"
        )
    typer.echo(f"Library: '{lib}' version is valid...")


@app.command()
def check_library_modified(lib: str):
    libraries: List[str] = validate_libraries(libraries)
    assert lib in libraries, "Invalid library name provided"
    if get_modified_libraries([lib]):
        typer.echo(f"Library: '{lib}' modified")
        raise typer.Abort(
            f"library '{lib}' modified"
        )
    typer.echo(f"Library: '{lib}' unmodified...")


@app.command()
def check_project_modified(project: str):
    projects: List[str] = get_projects()
    assert project in projects, "Invalid project name provided"
    if get_modified_projects([project]):
        typer.echo(f"Project: '{project}' modified")
        raise typer.Abort(
            f"Project: '{project}' modified"
        )
    typer.echo(f"Project: '{project}' unmodified...")


@app.command()
def bump_librariy_version():
    library: str = prompt_library()
    typer.echo(f"Bumping version for {library} library...")
    lib_type: str = get_library_type(library)
    # Work around to bump uv version until uv version managment function is added
    run_system_command(
        f"""cd libs/{lib_type}/{library} && \\
        VERSION=$(uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version) && \\
        VERSION=$(echo $VERSION | awk -F. '/[0-9]+\\./{{$NF++;print}}' OFS=.) && \\
        uvx --from=toml-cli toml set --toml-path=pyproject.toml project.version $VERSION
        """
    )


@app.command()
def lint():
    typer.echo("Running linting for hextech...")
    run_system_command("cd tools/hextech && make lint")
    typer.echo("Running linting for projects...")
    projects: List[str] = get_projects()
    for project in projects:
        typer.echo(f"Running linting for {project} project...")
        run_system_command(f"cd projects/{project} && make lint")
    typer.echo("Running linting for libraries...")
    libraries: List[str] = get_libraries()
    for lib in libraries:
        lib_type: str = get_library_type(lib)
        typer.echo(f"Running linting for {lib_type}/{lib} library...")
        run_system_command(f"cd libs/{lib_type}/{lib} && make lint")


@app.command()
def deploy_libs(
    libraries: Optional[List[str]] = None,
    check_modified: bool = False,
    no_input: bool = False,
):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=no_input)
    if libraries and "" in libraries:
        libraries = libraries.remove("")

    publish_libs(config, libraries=libraries, check_modified=check_modified)


@app.command()
def deploy_projects(
    env: str,
    projects: Optional[List[str]] = None,
    check_modified: bool = False,
    no_input: bool = False,
):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=no_input)
    if projects and "" in projects:
        projects = projects.remove("")

    deploy_projects_command(
        env, config, projects=projects, check_modified=check_modified, no_input=no_input
    )


@app.command()
def start_infra():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    start_infra_command(config)


@app.command()
def stop_infra():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    stop_infra_command(config)


@app.command()
def bastion(
    env: Annotated[Optional[str], typer.Argument()] = None,
    project: Annotated[Optional[str], typer.Argument()] = None,
):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    env: str = env or prompt_environment()
    project: str = project or prompt_project()
    bastion_ssh_tunnel(config, env, project)


@app.command()
def migrate_db(
    env: Annotated[Optional[str], typer.Argument()] = None,
    project: Annotated[Optional[str], typer.Argument()] = None,
):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    env: str = env or prompt_environment()
    project: str = project or prompt_project()
    migrate_db_func(config, env, project)


@app.command()
def update_projects_from_template():
    # Get list of changes to template/project
    with contextlib.chdir("templates/project/{{cookiecutter.project_name}}"):
        os.system("git format-patch --relative main --stdout > ../../../patch")

    for project in get_projects():
        os.system(f"git apply --3way --directory projects/{project}/ ./patch")

    os.system("rm patch")


if __name__ == "__main__":
    app()
