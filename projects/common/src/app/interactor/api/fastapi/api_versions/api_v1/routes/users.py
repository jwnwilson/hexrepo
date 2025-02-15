from uuid import UUID
from fastapi import Depends, Response, status
from fastapi.responses import JSONResponse
from hexrepo_api import CrudRouter
from hexrepo_cloud.auth.interface import AuthAdapter, UserDTO
from app.adaptor.db.interface import UOW
from app.domain.user import UserPermissionCreateDTO, UserPermissionDTO


from ......dependencies import get_auth, get_current_user, get_uow, get_uow_ro

router_v1 = CrudRouter(
    db_dependency=get_uow,
    db_dependency_ro=get_uow_ro,
    # auth_adaptor=get_current_user,
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


@router_v1.delete("/{id}", include_in_schema=True)
def delete(id: UUID, uow: UOW=Depends(get_uow), auth: AuthAdapter = Depends(get_auth)) -> Response:
    user: UserDTO = uow.user.read(id)
    auth.delete_user(user)
    uow.user.delete(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
