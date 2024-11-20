import json
from urllib.parse import quote  

from monorepo_storage.secrets.aws import AWSSecretAdaptor
from app.config import config


def get_db_url_from_aws_secret() -> str:
    password_data: str = AWSSecretAdaptor().get_secret(config.DB_PASSWORD_SECRET_NAME)
    password: str = json.loads(password_data)["password"]
    password = quote(password)
    return config.DB_URL.format(password=password)