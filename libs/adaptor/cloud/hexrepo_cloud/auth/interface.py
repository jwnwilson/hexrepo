from abc import ABC, abstractmethod
from typing import Dict, Optional

from pydantic import BaseModel
from hexrepo_db.interface import UOW, Repository


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
    def login(self, user: UserLogin) -> Dict:
        pass

    @abstractmethod
    def logout(self, token: str) -> None:
        pass

    @abstractmethod
    def register(self, user: UserSignupDTO) -> SignupResponse:
        pass

    @abstractmethod
    def verify(self, token: str) -> None:
        pass

    @abstractmethod
    def delete_user(self, user: UserDTO) -> None:
        pass


class UserUOW(UOW):
    @abstractmethod
    def user(self) -> Repository:
        pass