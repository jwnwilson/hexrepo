import logging
from collections.abc import Generator
from app.domain.user import UserPermissionDTO
from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from hexrepo_cloud.auth.cognito.fastapi_cognito import JWTAuthorizationCredentials
from hexrepo_cloud.auth.cognito import get_jwt_token
from hexrepo_cloud.auth.interface import AuthAdapter
from hexrepo_db.interface import PaginatedData
from hexrepo_task import QueueAdaptor, SqsQueueAdaptor
from hexrepo_task.adaptor.db import QueueUOW
from hexrepo_db.sql import get_sql_db_url

from app.config import config
from app.adaptor.db.sql import SqlUOW

logger = logging.getLogger(__name__)


def get_uow() -> Generator[SqlUOW, None, None]:
    uow = SqlUOW(db_url=get_sql_db_url())
    with uow.transaction():
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
    uow: SqlUOW = Depends(get_uow),
) -> UserPermissionDTO:
    try:
        # Run authorization logic here
        user_data: PaginatedData = uow.user.read_multi(username=credentials.claims["username"])
        if not user_data.results:
            raise ValueError("User not found")
        user: UserPermissionDTO = user_data.results[0]
        return user
    except KeyError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Username missing")
