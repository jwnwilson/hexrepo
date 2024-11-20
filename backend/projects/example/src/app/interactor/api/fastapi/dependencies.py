from collections.abc import Generator
from monorepo_db import UOW

from app.adaptor.db.sql import SqlUOW
from app.config import config
from ...aws.secrets import get_db_url_from_aws_secret


def get_db_url():
    # Running on the cloud
    if config.DB_PASSWORD_SECRET_NAME:
        if config.CLOUD_PROVIDER.upper() == "AWS":
            return get_db_url_from_aws_secret()
        else:
            raise NotImplementedError(f"No secret manager implemented for Cloud provider {config.CLOUD_PROVIDER}")
    # Running locally
    else:
        return config.DB_URL



def get_uow() -> Generator[UOW, None, None]:
    uow = SqlUOW(db_url=get_db_url())
    with uow.transaction():
        yield uow
