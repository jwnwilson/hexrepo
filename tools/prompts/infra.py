import typer


def prompt_setup_tf() -> bool:
    return typer.confirm("Would you like to setup Terraform state?")


def prompt_setup_lib_infra() -> bool:
    return typer.confirm("Would you like to setup infrastructure for libraries?")


def prompt_deploy_libs() -> bool:
    return typer.confirm("Would you like to deploy libraries?")