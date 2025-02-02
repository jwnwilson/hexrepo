
from sqlalchemy import UUID, Column, ForeignKey, String, Table, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from app.domain.user import GroupPermissionDTO
from .permission import PermissionGroupsTable, PermissionUsersTable as PermissionUsersTable


# Joining table to link groups to users
class UserGroupsTable(Base):
    __tablename__ = "user_groups"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    group_id: Mapped[UUID] = mapped_column(ForeignKey("group.id"))


class GroupTable(Base):
    __tablename__ = "group"

    name: Mapped[str] = mapped_column(String)
    users: Mapped[list["UserTable"]] = relationship(
        "UserTable",
        secondary=UserGroupsTable.__table__,
        overlaps="users"
    )
    permissions: Mapped[list["PermissionTable"]] = relationship(
        "PermissionTable",
        secondary=PermissionGroupsTable.__table__,
        overlaps="groups"
    )

    def __str__(self) -> str:
        return f"{self.name} | {self.id}"


class GroupRepository(SQLRepository):
    model = GroupTable
    model_dto = GroupPermissionDTO
