from abc import ABC, abstractmethod
from typing import Dict, Optional

from pydantic import BaseModel


class UserDTO(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    confirmation_code: Optional[str] = None


class AuthAdapter(ABC):
    @abstractmethod
    def login(self, user: UserDTO) -> Dict:
        pass
    
    @abstractmethod
    def logout(self, token: str) -> None:
        pass
    
    @abstractmethod
    def register(self, user: UserDTO) -> Dict:
        pass

    @abstractmethod
    def verify(self, token: str) -> None:
        pass

    