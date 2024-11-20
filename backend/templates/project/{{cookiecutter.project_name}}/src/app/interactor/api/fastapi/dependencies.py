from collections.abc import Generator
import json
from monorepo_db import UOW
from monorepo_storage import AWSSecretAdaptor

from app.adaptor.db.sql import SqlUOW
from app.config import config


def get_db_url():
    # Running on the cloud
    if config.DB_PASSWORD_SECRET_NAME:
        if config.CLOUD_PROVIDER.upper() == "AWS":
            password_data: str = AWSSecretAdaptor().get_secret(config.DB_PASSWORD_SECRET_NAME)
            password: str = json.loads(password_data)["password"]
            db_url =  config.DB_URL.format(password=password)
            return db_url
        else:
            raise NotImplementedError(f"No secret manager implemented for Cloud provider {config.CLOUD_PROVIDER}")
    # Running locally
    else:
        return config.DB_URL



def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_db_url())
    with uow.transaction():
        yield uow
