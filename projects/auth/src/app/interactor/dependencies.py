import logging
from collections.abc import Generator
from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from hexrepo_db import UOW

from app.domain.user import UserPermissionDTO, UserManager
from hexrepo_cloud.auth.cognito.fastapi_cognito import JWTAuthorizationCredentials
from hexrepo_cloud.auth.cognito import get_jwt_token
from hexrepo_cloud.auth.interface import AuthAdapter
from app.adaptor.db.nosql import DynamoUOW
from app.config import config

logger = logging.getLogger(__name__)


def get_uow() -> Generator[UOW, None, None]:
    # Leave empty string to use aws env vars
    uow = DynamoUOW(db_url=config.DB_URL)
    yield uow


def get_auth(
    uow: DynamoUOW = Depends(get_uow),
) -> Generator[AuthAdapter, None, None]:
    from hexrepo_cloud.auth.cognito.auth_adaptor import CognitoAuthAdapter

    auth = CognitoAuthAdapter(uow=uow)
    yield auth


def get_current_user(
    credentials: JWTAuthorizationCredentials = Depends(get_jwt_token),
    uow: DynamoUOW = Depends(get_uow),
) -> UserPermissionDTO:
    try:
        user_manager: UserManager = UserManager(uow=uow)
        # Run authorization logic here
        user: UserPermissionDTO = user_manager.read_by_username(credentials.claims["username"])
        return user
    except KeyError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Username missing")
