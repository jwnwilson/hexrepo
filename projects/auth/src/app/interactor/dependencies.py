import logging
import uuid
from collections.abc import Generator
from pydantic import BaseModel

from app.config import config
from hexrepo_db import UOW
from app.adaptor.db.nosql import DynamoUOW
from app.adaptor.auth.interface import AuthAdapter

logger = logging.getLogger(__name__)


def get_uow() -> Generator[UOW, None, None]:
    # Leave empty string to use aws env vars
    uow = DynamoUOW(db_url=config.DB_URL)
    yield uow


def get_auth() -> Generator[AuthAdapter, None, None]:
    from app.adaptor.auth.cognito import CognitoAuthAdapter

    auth = CognitoAuthAdapter()
    yield auth
