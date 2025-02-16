import logging
from collections.abc import Generator

from fastapi import Depends, HTTPException
from hexrepo_cloud.auth.cognito import get_jwt_token
from hexrepo_cloud.auth.cognito.fastapi_cognito import JWTAuthorizationCredentials
from hexrepo_cloud.auth.interface import AuthAdapter
from hexrepo_db.interface import PaginatedData
from hexrepo_db.sql import get_sql_db_url
from hexrepo_task import QueueAdaptor, SqsQueueAdaptor
from hexrepo_task.adaptor.db import QueueUOW
from starlette.status import HTTP_403_FORBIDDEN

from app.adaptor.db.sql import SqlUOW
from app.config import config
from app.domain.user import UserPermissionDTO, get_user

logger = logging.getLogger(__name__)


def get_uow() -> Generator[SqlUOW, None, None]:
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
        yield uow


def get_uow_ro(uow: SqlUOW = Depends(get_uow)) -> Generator[SqlUOW, None, None]:
    if config.READ_REPLICA_ENABLED:
        uow = SqlUOW(db_url=get_sql_db_url(read_only=True))
        with uow.transaction():
            yield uow
    else:
        yield uow


def get_queue_uow() -> Generator[QueueUOW, None, None]:
    uow: QueueUOW = QueueUOW()
    yield uow


def get_task_queue() -> Generator[QueueAdaptor, None, None]:
    queue = SqsQueueAdaptor(queue="hexrepo-tasks")
    yield queue


def get_auth(
    uow: SqlUOW = Depends(get_uow),
) -> Generator[AuthAdapter, None, None]:
    from hexrepo_cloud.auth.cognito.auth_adaptor import CognitoAuthAdapter

    auth = CognitoAuthAdapter(uow=uow)
    yield auth


def get_current_user(
    credentials: JWTAuthorizationCredentials = Depends(get_jwt_token),
    uow: SqlUOW = Depends(get_uow_ro),
) -> UserPermissionDTO:
    try:
        return get_user(uow, credentials.claims["username"])
    except KeyError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Username missing")


def get_superadmin_user(
    credentials: JWTAuthorizationCredentials = Depends(get_jwt_token),
    uow: SqlUOW = Depends(get_uow_ro),
) -> UserPermissionDTO:
    user: UserPermissionDTO = get_current_user(credentials, uow)
    if not user.is_superuser():
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Admin access required")
    return user