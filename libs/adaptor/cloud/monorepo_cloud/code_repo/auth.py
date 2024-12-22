from monorepo_cloud.code_repo.aws import authenticate_code_artiface
from monorepo_cloud.config import AWSConfig


def authenticate_repo(config: AWSConfig) -> str:
    auth_token: str = ""
    # Authenticate to the library repo
    auth_token = authenticate_code_artiface(config)

    return auth_token
