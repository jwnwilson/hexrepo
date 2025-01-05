import typer
from hexrepo_cloud.code_repo import authenticate_repo

from hextech.config import HexrepoConfig


def authenticate_lib_repo(config: HexrepoConfig) -> str:
    auth_token = ""
    # Authenticate to the library repo
    if config.cloud_provider == "aws":
        typer.echo("Authenticating with cloud provider...")
        auth_token = authenticate_repo(config.cloud_provider_config)
        typer.echo("Authentication successful.")
        config.set_env_var("HEXREPO_LIB_REPO_PASSWORD", auth_token)
        config.set_env_var("HEXREPO_LIB_REPO_USERNAME", "aws")
    return auth_token
