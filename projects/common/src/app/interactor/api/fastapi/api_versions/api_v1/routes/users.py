from app.domain.user import UserPermissionCreateDTO, UserPermissionDTO
from fastapi import Depends, Response, status
from fastapi.responses import JSONResponse
from hexrepo_api import CrudRouter

from ......dependencies import get_current_user, get_uow

router_v1 = CrudRouter(
    db_dependency=get_uow,
    auth_adaptor=get_current_user,
    repository="user",
    methods=["CREATE", "READ", "UPDATE", "DELETE"],
    response_schema=UserPermissionDTO,
    create_schema=UserPermissionCreateDTO,
    update_schema=UserPermissionDTO,
)


@router_v1.get("/me/", include_in_schema=True)
def user(user: UserPermissionDTO = Depends(get_current_user)) -> JSONResponse:
    return Response(
        content=user.model_dump_json(),
        status_code=status.HTTP_200_OK,
        headers={"content-type": "application/json"}
    )
