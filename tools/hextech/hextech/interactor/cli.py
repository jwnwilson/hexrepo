from typing import TYPE_CHECKING, List, Optional

import typer
from typing_extensions import Annotated

if TYPE_CHECKING:
    pass

app = typer.Typer()


@app.command()
def setup():
    from .commands import setup

    setup()


@app.command()
def destroy():
    from .commands import destroy

    destroy()


@app.command()
def create_library():
    from .commands import create_library

    create_library()


@app.command()
def create_project():
    from .commands import create_project

    create_project()


@app.command()
def add_library():
    from .commands import add_library

    add_library()


@app.command()
def shared_infra_plan():
    from .commands import shared_infra_plan

    shared_infra_plan()


@app.command()
def shared_infra_apply():
    from .commands import shared_infra_apply

    shared_infra_apply()


@app.command()
def env_infra_plan(env: str):
    from .commands import env_infra_plan

    env_infra_plan(env)


@app.command()
def env_infra_apply(env: str):
    from .commands import env_infra_apply

    env_infra_apply(env)


@app.command()
def test_projects(run_all: bool = True):
    from .commands import test_projects

    test_projects(run_all)


@app.command()
def test_libs(libraries: Optional[List[str]] = None):
    from .commands import test_libs

    test_libs(libraries)


@app.command()
def test_tools():
    from .commands import test_tools

    test_tools()


@app.command()
def check_library_bump(library: str):
    from .commands import check_library_bump

    check_library_bump(library)


@app.command()
def check_library_modified(library: str):
    from .commands import check_library_modified

    check_library_modified(library)


@app.command()
def check_project_modified(project: str):
    from .commands import check_project_modified

    check_project_modified(project)


@app.command()
def bump_library_version():
    from .commands import bump_library_version

    bump_library_version()


@app.command()
def lint():
    from .commands import lint

    lint()


@app.command()
def deploy_libs(
    libraries: Optional[List[str]] = None,
    check_modified: bool = False,
    no_input: bool = False,
):
    from .commands import deploy_libs

    deploy_libs(libraries, check_modified, no_input)


@app.command()
def deploy_projects(
    env: str,
    projects: Optional[List[str]] = None,
    check_modified: bool = False,
    no_input: bool = False,
):
    from .commands import deploy_projects

    deploy_projects(env, projects, check_modified, no_input)


@app.command()
def start_infra():
    from .commands import start_infra

    start_infra()


@app.command()
def stop_infra():
    from .commands import stop_infra

    stop_infra()


@app.command()
def bastion(
    env: Annotated[Optional[str], typer.Argument()] = None,
    project: Annotated[Optional[str], typer.Argument()] = None,
):
    from .commands import bastion

    bastion(env, project)


@app.command()
def migrate_db(
    env: Annotated[Optional[str], typer.Argument()] = None,
    project: Annotated[Optional[str], typer.Argument()] = None,
):
    from .commands import migrate_db

    migrate_db(env, project)


@app.command()
def create_user(
    env: Annotated[Optional[str], typer.Argument()] = None,
    project: Annotated[Optional[str], typer.Argument()] = None,
):
    from .commands import create_user

    create_user(env)


@app.command()
def create_permissions(
    env: Annotated[Optional[str], typer.Argument()] = None,
    project: Annotated[Optional[str], typer.Argument()] = None,
):
    from .commands import create_permissions

    create_permissions(env)


@app.command()
def update_projects_from_template():
    from .commands import update_projects_from_template

    update_projects_from_template()


if __name__ == "__main__":
    app()
