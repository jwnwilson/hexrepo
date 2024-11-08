import os
from cookiecutter.main import cookiecutter
import typer


app = typer.Typer()


@app.command()
def create_be_library():
    library_type: str = typer.prompt("Please enter the library type (adaptor/interactor)")
    if library_type not in ["adaptor", "interactor"]:
        typer.echo("Invalid library type. Please enter either 'adaptor' or 'interactor'.")
        return

    # CD to libs/src/adaptor or libs/src/interactor folder
    os.chdir(f"backend/libs/src/{library_type}")
    # Run cookie cutter command to copy template
    cookiecutter("../../../templates/library")


@app.command()
def create_be_project():
    # CD to projects folder
    os.chdir(f"backend/projects")
    # Run cookie cutter command to copy template
    cookiecutter("../../../templates/project")


@app.command()
def add_be_library():
    # Install library locally in poetry dev group

    # Install library from repo if available

    # Call library install hook
    pass


if __name__ == "__main__":
    app()