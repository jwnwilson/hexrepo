import logging
from collections.abc import Generator

from hexrepo_db import UOW

from app.adaptor.auth.cognito import get_current_user as get_current_user
from app.adaptor.auth.cognito import get_jwt_token as get_jwt_token
from app.adaptor.auth.interface import AuthAdapter
from app.adaptor.db.nosql import DynamoUOW
from app.config import config

logger = logging.getLogger(__name__)


def get_uow() -> Generator[UOW, None, None]:
    # Leave empty string to use aws env vars
    uow = DynamoUOW(db_url=config.DB_URL)
    yield uow


def get_auth() -> Generator[AuthAdapter, None, None]:
    from app.adaptor.auth.cognito.auth_adaptor import CognitoAuthAdapter

    auth = CognitoAuthAdapter()
    yield auth
