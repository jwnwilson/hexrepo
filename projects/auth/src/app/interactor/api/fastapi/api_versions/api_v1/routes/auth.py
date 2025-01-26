from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.adaptor.auth.interface import UserDTO, AuthAdapter
from app.interactor.dependencies import get_auth

router_v1 = APIRouter()


@router_v1.post("/", include_in_schema=True)
def signup(user: UserDTO, auth: AuthAdapter = Depends(get_auth)) -> JSONResponse:
    response = auth.register(user)
    return JSONResponse(
        content=response,
        status_code=status.HTTP_200_OK,
    )


@router_v1.post("/", include_in_schema=True)
def verify(user: UserDTO, auth: AuthAdapter = Depends(get_auth)) -> JSONResponse:
    response = auth.verify(user)
    return JSONResponse(
        content=response,
        status_code=status.HTTP_200_OK,
    )


@router_v1.post("/", include_in_schema=True)
def login(user: UserDTO, auth: AuthAdapter = Depends(get_auth)) -> JSONResponse:
    response = auth.login(user)
    return JSONResponse(
        content=response,
        status_code=status.HTTP_200_OK,
    )


@router_v1.post("/", include_in_schema=True)
def logout(user: UserDTO, auth: AuthAdapter = Depends(get_auth)) -> JSONResponse:
    response = auth.logout(user)
    return JSONResponse(
        content=response,
        status_code=status.HTTP_200_OK,
    )
