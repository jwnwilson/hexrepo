from typing import List

import typer


def prompt_config_setup():
    print("Do you want to setup project config?")
    print("1 - Yes")
    print("2 - No")
    config_setup_option: str = typer.prompt("Choose from [1, 2]")
    try:
        return {"1": True, "2": False}[config_setup_option]
    except KeyError:
        typer.echo("Invalid option, please select an option: 1, 2.")
        return


def prompt_environments() -> List[str]:
    create_env: bool = True
    environments: List[str] = []
    while create_env:
        env: str = typer.prompt(
            "Please enter name of environment to create:", default="dev,prod"
        )
        environments += env.split(",")
        typer.echo(f"Current environments to create: {environments}")
        create_env: bool = typer.confirm("Add another environment?")

    return environments
