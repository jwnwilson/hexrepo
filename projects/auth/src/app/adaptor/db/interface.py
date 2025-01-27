from hexrepo_db.nosql import BaseDynamoUOW, DynamoRepository


class UserUOW(BaseDynamoUOW):
    @property
    def user(self) -> DynamoRepository:
        raise NotImplementedError
    

