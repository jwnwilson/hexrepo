from app.adaptor.auth.exceptions import InvalidPasswordException, UserExistsException
from app.adaptor.auth.interface import (
    AuthAdapter,
    SignupResponse,
    UserDTO,
    UserLogin,
    UserSignupDTO,
    UserVerifyDTO,
)
from app.interactor.dependencies import get_auth
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse

router_v1 = APIRouter()


@router_v1.post("/signup", include_in_schema=True)
def signup(user: UserSignupDTO, auth: AuthAdapter = Depends(get_auth)) -> JSONResponse:
    try:
        response: SignupResponse = auth.register(user)
    except (InvalidPasswordException, UserExistsException) as err:
        raise HTTPException(status_code=400, detail=str(err))
    return JSONResponse(
        content=response.model_dump(),
        status_code=status.HTTP_200_OK,
    )


@router_v1.post("/verify", include_in_schema=True)
def verify(user: UserVerifyDTO, auth: AuthAdapter = Depends(get_auth)) -> JSONResponse:
    response = auth.verify(user)
    return JSONResponse(
        content=response,
        status_code=status.HTTP_200_OK,
    )


@router_v1.post("/login", include_in_schema=True)
def login(user: UserLogin, auth: AuthAdapter = Depends(get_auth)) -> JSONResponse:
    response = auth.login(user)
    return JSONResponse(
        content=response,
        status_code=status.HTTP_200_OK,
    )


@router_v1.post("/logout", include_in_schema=True)
def logout(token: str, auth: AuthAdapter = Depends(get_auth)) -> JSONResponse:
    auth.logout(token)
    return Response(
        status_code=status.HTTP_200_OK,
    )
