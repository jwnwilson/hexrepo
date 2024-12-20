from typing import List
import typer

from hextech.domain.project import get_environments, get_projects


def prompt_cloud_provider() -> str:
    print("Please enter cloud provider:")
    print("1 - aws")
    # print("2 - gcp")
    # print("3 - azure")
    cloud_provider_optio : str = typer.prompt("Choose from [1]")
    try:
        cloud_provider = {"1": "aws"}[cloud_provider_optio]
    except KeyError:
        typer.echo("Invalid cloud provider, please select an option, 1")
        return
    return cloud_provider

def prompt_library_type() -> str:
    print("Please enter the library type:")
    print("1 - adaptor")
    print("2 - interactor")
    library_option: str = typer.prompt("Choose from [1, 2]")
    try:
        library_type = {"1": "adaptor", "2": "interactor"}[library_option]
    except KeyError:
        typer.echo("Invalid library type, please select an option: 1, 2.")
        return
    return library_type


def prompt_shell_file() -> str:
    print("Please enter shell file:")
    print("1 - ~/.bashrc")
    print("2 - ~/.zshrc")
    shell_option: str = typer.prompt("Choose from [1, 2]")
    try:
        shell_file = {"1": "~/.bashrc", "2": "~/.zshrc"}[shell_option]
    except KeyError:
        typer.echo("Invalid shell file, please select an option: 1, 2.")
        return
    return shell_file


def prompt_environment() -> str:
    print("Please enter environment:")
    enironments: List[str] = get_environments()
    env_map: List[str] = {str(i+1): env for i, env in enumerate(enironments)}
    options = "\n".join([f"{i} - {project}" for i, project in env_map.items()])
    selection: str = typer.prompt(f"Choose from [{options}]", default="1")
    try:
        environment = env_map[selection]
    except KeyError:
        typer.echo(f"Invalid environment, please select an option: {options}.")
        return
    return environment


def prompt_project() -> str:
    print("Please enter project:")
    projects: List[str] = get_projects()
    project_map: List[str] = {str(i+1): project for i, project in enumerate(projects)}
    options = "\n".join([f"{i} - {project}" for i, project in project_map.items()])
    selection: str = typer.prompt(f"Choose from [{options}]", default="1")
    try:
        project = project_map[selection]
    except KeyError:
        typer.echo(f"Invalid project, please select an option: {options}.")
        return
    return project
