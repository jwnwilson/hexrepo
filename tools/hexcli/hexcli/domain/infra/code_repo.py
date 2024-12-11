import typer
from tools.hexcli.hexcli.config import MonorepoConfig
from monorepo_cloud.code_repo import authenticate_repo


def authenticate_lib_repo(config: MonorepoConfig) -> str:
    auth_token = ""
    # Authenticate to the library repo
    if config.cloud_provider == "aws":
        typer.echo("Authenticating with cloud provider...")
        auth_token = authenticate_repo(config)
        typer.echo("Authentication successful.")
        config.set_env_var( "MONOREPO_LIB_REPO_PASSWORD", auth_token)
        config.set_env_var("MONOREPO_LIB_REPO_USERNAME", "aws")
    return auth_token
