from hexrepo_db.sql import BaseSqlUOW
from .models.user import UserRepository

class SqlUOW(BaseSqlUOW):

    @property
    def user(self) -> UserRepository:
        return UserRepository(self.session)