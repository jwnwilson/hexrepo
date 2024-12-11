from hexcli.logic.config import MonorepoConfig
from monorepo_cloud.code_repo import authenticate_repo


def authenticate_lib_repo(config: MonorepoConfig) -> str:
    # Authenticate to the library repo
    if config.cloud_provider == "aws":
        auth_token = authenticate_repo(config)
        config.set_env_var( "MONOREPO_LIB_REPO_PASSWORD", auth_token)
        config.set_env_var("MONOREPO_LIB_REPO_USERNAME", "aws")