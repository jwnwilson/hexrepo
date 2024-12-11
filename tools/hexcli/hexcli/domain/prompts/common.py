import typer


def prompt_cloud_provider() -> str:
    print("Please enter cloud provider:")
    print("1 - aws")
    print("2 - gcp")
    print("3 - azure")
    cloud_provider_optio : str = typer.prompt("Choose from [1, 2, 3]")
    try:
        cloud_provider = {"1": "aws", "2": "gcp", "3": "azure"}[cloud_provider_optio]
    except KeyError:
        typer.echo("Invalid cloud provider, please select an option, 1, 2 or 3.")
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