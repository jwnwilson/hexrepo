from fastapi import Depends, status
from fastapi.responses import JSONResponse
from hexrepo_api import CrudRouter

from app.adaptor.auth.interface import UserDTO
from app.adaptor.db.nosql.models.user import UserPermissionDTO

from ......dependencies import get_current_user, get_uow

router_v1 = CrudRouter(
    db_dependency=get_uow,
    repository="user",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=UserPermissionDTO,
    create_schema=UserPermissionDTO,
    update_schema=UserPermissionDTO,
)


@router_v1.get("/me/", include_in_schema=True)
def user(user: UserPermissionDTO = Depends(get_current_user)) -> JSONResponse:
    return JSONResponse(
        content=user.model_dump(),
        status_code=status.HTTP_200_OK,
    )
