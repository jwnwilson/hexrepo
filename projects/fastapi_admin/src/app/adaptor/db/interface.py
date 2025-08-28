from hexrepo_db.interface import UOW as BaseUOW
from hexrepo_db.interface import Repository


class UOW(BaseUOW):
    @property
    def user(self) -> Repository:
        raise NotImplementedError

    @property
    def group(self) -> Repository:
        raise NotImplementedError

    @property
    def permission(self) -> Repository:
        raise NotImplementedError

    @property
    def feature_flag(self) -> Repository:
        raise NotImplementedError

    @property
    def company(self) -> Repository:
        raise NotImplementedError
