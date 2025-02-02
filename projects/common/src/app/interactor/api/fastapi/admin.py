from fastapi import FastAPI
from sqladmin import Admin, ModelView

from app.config import config
from app.adaptor.db.sql.uow import SqlUOW
from app.adaptor.db.sql.models.user import UserTable


class UserAdmin(ModelView, model=UserTable):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    
    column_list = [
        UserTable.id,
        UserTable.username,
        UserTable.email,
    ]


def setup_admin(app: FastAPI):
    engine = SqlUOW(db_url=config.DB_URL).session_manager._engine
    admin: Admin = Admin(app, engine)

    admin.add_view(UserAdmin)