import os
import boto3

from tools.logic.env import set_env_var

def authenticate_lib_repo(cloud_provider: str, shell_file: str) -> str:
    # Authenticate to the library repo
    if cloud_provider == "aws":
        aws_account = os.environ.get("AWS_ACCOUNT")
        
        client = boto3.client('codeartifact')
        auth_token = client.get_authorization_token(
            domain="monorepo",
            domainOwner=aws_account
        )["authorizationToken"]
        set_env_var(shell_file, "MONOREPO_LIB_REPO_AUTH_TOKEN", auth_token)