import os
import typer


def run_system_command(command: str) -> None:
    return_code = os.system(command)
    if return_code != 0:
        typer.echo(f"System command failed: {command}")
        raise typer.Abort()
