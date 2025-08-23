import os
from contextlib import chdir
from typing import List, Optional

import copier
import typer
from typing_extensions import Annotated

from hextech.config import HexrepoConfig, get_or_create_config
from hextech.domain.infra.bastion import bastion_ssh_tunnel, ecs_exec_cli
from hextech.domain.infra.deployment import (
    apply_env_infra,
    create_shared_infra,
    destroy_env_infra,
    destroy_shared_infra,
    plan_env_infra_command,
    project_infra_apply,
    project_infra_plan,
    publish_libs,
    shared_infra_apply_command,
    shared_infra_plan_command,
)
from hextech.domain.infra.deployment import deploy_projects as deploy_projects_command
from hextech.domain.infra.deployment import migrate_db as migrate_db_func
from hextech.domain.infra.manage import start_infra_command, stop_infra_command
from hextech.domain.infra.storage import create_tf_state
from hextech.domain.infra.user import (
    create_user_permissions,
    create_user_with_permissions,
)
from hextech.domain.project import (
    cli_setup,
    get_libraries,
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
    prompt_project,
)
from hextech.domain.prompts.infra import (
    prompt_destroy,
    prompt_setup_project_infra,
    prompt_setup_shared_infra,
    prompt_setup_tf,
)
from hextech.domain.system import run_system_command


@cli_setup
def setup():
    # project config setup
    config: HexrepoConfig
    created_config: bool
    config, created_config = get_or_create_config()

    # Create initial terraform state infra
    if prompt_setup_tf():
        create_tf_state(config)

    # Setup initial infra for all projects
    if prompt_setup_shared_infra():
        create_shared_infra(config)
        for env in config.environments:
            apply_env_infra(config, env)


@cli_setup
def destroy():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    if prompt_destroy():
        for project in get_projects():
            run_system_command(f"cd projects/{project} && make tf_destroy")
        for env in config.environments:
            destroy_env_infra(config, env)
        destroy_shared_infra(config)


@cli_setup
def create_library():
    # CD to libs/adaptor or libs/interactor folder
    with chdir("libs"):
        # Run copier command to copy template
        lib_name: str = typer.prompt("Please Enter project folder name")
        copier.run_copy("../../templates/library", f"./{lib_name}")


@cli_setup
def create_project():
    project_name: str = typer.prompt("Please Enter project folder name")
    os.system("rm -r templates/project/.venv 2> /dev/null || echo > /dev/null")
    template_choice = typer.prompt(
        "Which project template would you like to use? \n  1.fastapi\n  2.django_ninja\n",
        default="1"
    )
    # Validate the choice
    if template_choice.lower() not in ["1", "2"]:
        typer.echo("Invalid choice. Please select '1' or '2'")
        raise typer.Exit(1)
    if template_choice.lower() == "1":
        template_path = "https://github.com/jwnwilson/fastapi_project_template.git"
    else:
        template_path = "https://github.com/jwnwilson/ninja_project_template.git"
    # CD to projects folder
    with chdir("projects"):
        # Run copier command to copy template
        copier.run_copy(
            template_path, f"./{project_name}",
            data={
                "project_name": project_name,
            }
        )
        # Setup infra for service
        if prompt_setup_project_infra():
            with chdir(project_name):
                typer.echo("Setting up initial infrastructure...")
                run_system_command("make tf_setup ENVIROMENT=default")
                typer.echo("Initial infrastructure setup complete.")


@cli_setup
def add_library():
    library: str = prompt_library()
    project: str = prompt_project()
    # Install library from repo if available
    install_library_in_project(library, project)


@cli_setup
def shared_infra_plan():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    shared_infra_plan_command(config)


@cli_setup
def shared_infra_apply():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    shared_infra_apply_command(config, no_input=True)


@cli_setup
def env_infra_plan(env: str):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    plan_env_infra_command(config, env)


@cli_setup
def env_infra_apply(env: str, no_input: bool = True):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=no_input)
    apply_env_infra(config, env, no_input=no_input)


@cli_setup
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


@cli_setup
def test_libs(libraries: Optional[List[str]] = None):
    libraries: List[str] = validate_libraries(libraries)

    for lib in libraries:
        typer.echo(f"Running linting for {lib} library...")
        run_system_command(f"cd libs/{lib} && make lint_check")
        typer.echo(f"Running tests for {lib} library...")
        run_system_command(f"cd libs/{lib} && make test")


@cli_setup
def test_tools():
    typer.echo("Running tests for hextech...")
    run_system_command("cd tools/hextech && make test")


@cli_setup
def check_library_bump(library: str):
    validate_libraries([library])
    if library_version_bump_required(library):
        typer.echo(f"Library: '{library}' needs version bump")
        raise typer.Abort(
            f"library '{library}' needs version bump, (please commit version bump)"
        )
    typer.echo(f"Library: '{library}' version is valid...")


@cli_setup
def check_library_modified(library: str):
    validate_libraries([library])
    if get_modified_libraries([library]):
        typer.echo(f"Library: '{library}' modified")
        raise typer.Abort(f"library '{library}' modified")
    typer.echo(f"Library: '{library}' unmodified...")


@cli_setup
def check_project_modified(project: str):
    projects: List[str] = get_projects()
    assert project in projects, "Invalid project name provided"
    if get_modified_projects([project]):
        typer.echo(f"Project: '{project}' modified")
        raise typer.Abort(f"Project: '{project}' modified")
    typer.echo(f"Project: '{project}' unmodified...")


def _bump_library_version(library: str):
    run_system_command(
        f"""cd libs/{library} && \\
        VERSION=$(uvx --from=toml-cli toml get --toml-path=pyproject.toml project.version) && \\
        VERSION=$(echo $VERSION | awk -F. '/[0-9]+\\./{{$NF++;print}}' OFS=.) && \\
        uvx --from=toml-cli toml set --toml-path=pyproject.toml project.version $VERSION
        """
    )


@cli_setup
def bump_library_version():
    library: str = prompt_library()
    typer.echo(f"Bumping version for {library} library...")
    # Work around to bump uv version until uv version managment function is added
    _bump_library_version(library)


@cli_setup
def bump_all_library_versions():
    all_libraries: List[str] = get_libraries()
    for library in all_libraries:
        typer.echo(f"Bumping version for {library} library...")
        # Work around to bump uv version until uv version managment function is added
        _bump_library_version(library)


@cli_setup
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
        typer.echo(f"Running linting for {lib} library...")
        run_system_command(f"cd libs/{lib} && make lint")


@cli_setup
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


@cli_setup
def infra_plan_project(env: str, project: str):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    project_infra_plan(config, env, project)


@cli_setup
def infra_apply_project(env: str, project: str, no_input: bool = False):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    project_infra_apply(config, env, project, no_input=no_input)


@cli_setup
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


@cli_setup
def start_infra():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    start_infra_command(config)


@cli_setup
def stop_infra():
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    stop_infra_command(config)


@cli_setup
def bastion(
    env: Annotated[Optional[str], typer.Argument()] = None,
    project: Annotated[Optional[str], typer.Argument()] = None,
):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    env: str = env or prompt_environment()
    project: str = project or prompt_project()
    bastion_ssh_tunnel(config, env, project)


@cli_setup
def ecs_exec(
    env: Annotated[Optional[str], typer.Argument()] = None,
    project: Annotated[Optional[str], typer.Argument()] = None,
    command: Annotated[Optional[str], typer.Argument()] = None,
):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    env: str = env or prompt_environment()
    project: str = project or prompt_project()
    ecs_exec_cli(config, env, project, command)


@cli_setup
def migrate_db(
    env: Annotated[Optional[str], typer.Argument()] = None,
    project: Annotated[Optional[str], typer.Argument()] = None,
):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    env: str = env or prompt_environment()
    project: str = project or prompt_project()
    migrate_db_func(config, env, project)


@cli_setup
def create_user(
    env: Annotated[Optional[str], typer.Argument()] = None,
):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    env: str = env or prompt_environment()
    # Placeholder for creating user
    create_user_with_permissions(config, env)


@cli_setup
def create_permissions(
    env: Annotated[Optional[str], typer.Argument()] = None,
):
    config: HexrepoConfig
    config, _ = get_or_create_config(no_input=True)
    env: str = env or prompt_environment()
    # Placeholder for creating user
    create_user_permissions(config, env)


@cli_setup
def update_projects_from_template():
    project_name: str = typer.prompt("Please Enter project name")
    os.system(f"cd projects/{project_name} && copier update")
