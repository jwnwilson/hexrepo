
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from app.domain.user import GroupPermissionDTO


# Need join table on user and group

class PermissionTable(Base):
    __tablename__ = "group"

    name: Mapped[str] = mapped_column(String)


class GroupRepository(SQLRepository):
    model = PermissionTable
    model_dto = GroupPermissionDTO
