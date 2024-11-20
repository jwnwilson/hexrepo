import json
from monorepo_storage.secrets.aws import AWSSecretAdaptor
from config import config


def get_db_url_from_aws_secret() -> str:
    password_data: str = AWSSecretAdaptor().get_secret(config.DB_PASSWORD_SECRET_NAME)
    password: str = json.loads(password_data)["password"]
    return config.DB_URL.format(password=password)