
from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from hexrepo_db.sql.models.base_model import Base
from hexrepo_db.sql.repository import SQLRepository
from app.domain.user import GroupPermissionDTO

# Need join table on user

class GroupTable(Base):
    __tablename__ = "group"

    name: Mapped[str] = mapped_column(String)


class GroupRepository(SQLRepository):
    model = GroupTable
    model_dto = GroupPermissionDTO
