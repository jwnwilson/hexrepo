import os
from cookiecutter.main import cookiecutter
import typer


app = typer.Typer()


@app.command()
def create_be_library():
    print("Please enter the library type:")
    print("1 - adaptor")
    print("2 - interactor")
    library_option: str = typer.prompt("Choose from [1, 2]")
    if library_option not in ["1", "2"]:
        typer.echo("Invalid library type. Please enter either 'adaptor' or 'interactor'.")
        return
    library_type = {"1": "adaptor", "2": "interactor"}[library_option]

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
def add_be_library():
    # Install library locally in poetry dev group

    # Install library from repo if available

    # Call library install hook
    pass


@app.command()
def setup():
    # Save env vars in ~/.bashrc or ~/.zshrc
    # Pick ~/.bashrc or ~/.zshrc based on shell
    # Check if env vars exist
    # if not prompt user to enter them
    # Add envs to ~/.bashrc or ~/.zshrc
    pass


if __name__ == "__main__":
    app()