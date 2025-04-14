from typing import Any, Dict, List, Optional
from uuid import UUID

from hexrepo_cloud.auth.interface import AuthAdapter, UserSignupDTO
from hexrepo_db.exception import IntegrityError
from hexrepo_db.interface import PaginatedData
from loguru import logger
from pydantic import BaseModel

from app.adaptor.db.interface import UOW


class Token(BaseModel):
    access_token: str
    token_type: str


class EnvironmentDTO(BaseModel):
    id: UUID
    name: str
    config: Dict[str, Any] | None = None


class EnvironmentCreateDTO(BaseModel):
    name: str
    config: Dict[str, Any] | None = None


class UserPermissionCreateDTO(BaseModel):
    username: str
    name: str
    email: str
    permissions: List[Dict[str, Any]]
    groups: List[Dict[str, Any]]
    cognito_id: Optional[str] = None
    verified: bool
    company_id: Optional[UUID] = None


class UserPermissionDTO(UserPermissionCreateDTO):
    id: UUID

    def is_superuser(self) -> bool:
        permissions = set([x["name"] for x in self.permissions])
        return "superadmin" in permissions


class GroupPermissionDTO(BaseModel):
    id: UUID
    name: str
    users: List[Dict[str, Any]]
    permissions: List[Dict[str, Any]]


class PermissionDTO(BaseModel):
    id: UUID
    name: str
    users: List[Dict[str, Any]]
    groups: List[Dict[str, Any]]


class PermissionCreateDTO(BaseModel):
    name: str


class CompanyDTO(BaseModel):
    id: UUID
    name: str
    website: str


class CompanyCreateDTO(BaseModel):
    name: str
    website: str


class FeatureFlagBaseDTO(BaseModel):
    id: UUID
    name: str


class FeatureFlagBaseCreateDTO(BaseModel):
    name: str


class FeatureFlagEnvCreateDTO(BaseModel):
    env: str
    enabled: bool
    overrides: Dict[str, Any] | None = None


class FeatureFlagEnvDTO(BaseModel):
    id: UUID
    env: str
    enabled: bool
    overrides: Dict[str, Any] | None = None


class FeatureFlagCreateDTO(BaseModel):
    name: str
    enabled: bool = False


class FeatureFlagUpdateDTO(BaseModel):
    id: UUID
    name: str


class FeatureFlagDTO(BaseModel):
    id: UUID
    name: str
    environments: List[FeatureFlagEnvDTO] = []


class UserCreateDTO(BaseModel):
    username: str
    password: str
    email: str
    name: str


class PerrmissionManager:
    def __init__(self, uow: UOW):
        self.uow: UOW = uow

    def create_default_permissions(self) -> None:
        permission_list: List[str] = ["superadmin", "admin", "user"]
        try:
            for permission in permission_list:
                self.uow.permission.create(
                    PermissionCreateDTO(
                        name=permission,
                    )
                )
        except IntegrityError:
            logger.warning("Permissions already created")


# Create user class with link back to manager to do operations
class UserManager:
    def __init__(self, uow: UOW, auth: AuthAdapter):
        self.uow: UOW = uow
        self.auth: AuthAdapter = auth
        self.permission_manager: PerrmissionManager = PerrmissionManager(uow)

    def get_user(self, username: str) -> UserPermissionDTO:
        user_data: PaginatedData[UserPermissionDTO] = self.uow.user.read_multi(
            filters=dict(username=username)
        )
        if not user_data.results:
            raise ValueError("User not found")
        return user_data.results[0]

    def create_user(
        self, user_dto: UserCreateDTO, superuser: bool = False
    ) -> UserPermissionDTO:
        self.auth.register(
            UserSignupDTO(
                username=user_dto.username,
                password=user_dto.password,
                email=user_dto.email,
                name=user_dto.name,
            )
        )
        if superuser:
            try:
                superuser_permission: PermissionDTO = self.uow.permission.read_multi(
                    filters=dict(name="superadmin")
                ).results[0]
            except IndexError:
                logger.error("Superadmin permission not found")
            permissions: List[str] = [{"id": superuser_permission.id}]
        else:
            permissions: List[str] = []

        user = self.uow.user.create(
            UserPermissionCreateDTO(
                username=user_dto.username,
                email=user_dto.email,
                name=user_dto.name,
                permissions=permissions,
                groups=[],
                verified=True,
                company=None,
            )
        )
        return user

    def resend_verification(self, username: str):
        self.auth.send_verification_code(username)
