
from sqlalchemy import UUID, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from app.domain.user import GroupPermissionDTO


# Joining table to link permissions to groups
class PermissionGroupsTable(Base):
    __tablename__ = "permission_groups"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, autoincrement=True, nullable=False)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permission.id"))
    group_id: Mapped[UUID] = mapped_column(ForeignKey("group.id"))


# Joining table to link permissions to users
class PermissionUsersTable(Base):
    __tablename__ = "permission_users"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, autoincrement=True, nullable=False)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permission.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))


class PermissionTable(Base):
    __tablename__ = "permission"

    name: Mapped[str] = mapped_column(String)
    groups: Mapped[list["GroupTable"]] = relationship(
        "GroupTable",
        secondary=PermissionGroupsTable.__table__,
        overlaps="groups"
    )
    users: Mapped[list["UserTable"]] = relationship(
        "UserTable",
        secondary=PermissionUsersTable.__table__,
        overlaps="users"
    )


# class PermissionRepository(SQLRepository):
#     model = PermissionTable
#     model_dto = PermissionDTO
