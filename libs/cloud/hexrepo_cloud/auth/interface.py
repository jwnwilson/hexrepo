from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from fastapi import Request
from hexrepo_db.interface import UOW, Repository
from pydantic import BaseModel


class UserSignupDTO(BaseModel):
    username: str
    password: str
    name: str
    email: str


class SignupResponse(BaseModel):
    verified: bool
    verification_code_destination: str


class UserVerifyDTO(BaseModel):
    username: str
    confirmation_code: str


class UserDTO(BaseModel):
    username: str
    email: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class AuthAdapter(ABC):
    @abstractmethod
    def login(self, user: UserLogin) -> Dict[str, Any]:
        pass

    @abstractmethod
    def logout(self, token: str) -> None:
        pass

    @abstractmethod
    def register(self, user: UserSignupDTO) -> SignupResponse:
        pass

    @abstractmethod
    def send_verification_code(self, user: UserDTO) -> None:
        pass

    @abstractmethod
    def verify(self, token: str) -> None:
        pass

    @abstractmethod
    def delete_user(self, user: UserDTO) -> None:
        pass


class JWTAuthorizationCredentials(BaseModel):
    jwt_token: str
    header: Dict[str, str]
    claims: Dict[str, str | int]
    signature: str
    message: str


class FastapiJWTMiddleware:
    def verify_jwk_credentials(
        self, jwt_credentials: JWTAuthorizationCredentials
    ) -> bool:
        raise NotImplementedError

    def verify_jwt_token(self, jwt_token: str) -> JWTAuthorizationCredentials:
        raise NotImplementedError

    async def __call__(self, request: Request) -> Optional[JWTAuthorizationCredentials]:
        raise NotImplementedError


class UserUOW(UOW):
    @abstractmethod
    def user(self) -> Repository:
        pass
