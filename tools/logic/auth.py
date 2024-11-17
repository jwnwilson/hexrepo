import os
import boto3

from tools.logic.config import MonorepoConfig
from tools.logic.env import set_env_var

def authenticate_lib_repo(config: MonorepoConfig) -> str:
    # Authenticate to the library repo
    if config.cloud_provider == "aws":
        aws_account = config.cloud_provider_config.AWS_ACCOUNT
        
        client = boto3.client('codeartifact')
        auth_token = client.get_authorization_token(
            domain="monorepo",
            domainOwner=aws_account
        )["authorizationToken"]
        config.set_env_var( "MONOREPO_LIB_REPO_PASSWORD", auth_token)
        config.set_env_var("MONOREPO_LIB_REPO_USERNAME", "aws")