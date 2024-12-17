import boto3  # type: ignore

from ..config import AWSConfig


def authenticate_code_artiface(config: AWSConfig, domain: str = "monorepo") -> str:
    aws_account: str = config.AWS_ACCOUNT

    client = boto3.client("codeartifact")
    auth_token: str = client.get_authorization_token(
        domain=domain, domainOwner=aws_account
    )["authorizationToken"]

    return auth_token
