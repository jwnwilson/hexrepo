import argparse
from app.adaptor.db.interface import UOW
from app.domain.user import UserPermissionCreateDTO
from app.interactor.dependencies import get_uow
from hexrepo_task.interactor.event.app import resolve_dependencies


@resolve_dependencies
def create_superuser_cli(username:str, email: str, password:str, uow: UOW = get_uow()):
    """
    Create superuser CLI
    """
    print("Creating superuser...")
    # Need a way to use dependencies outside fastapi
    uow.user.create(UserPermissionCreateDTO(
        username=username,
        password=password,
        email=email
    ))
    print("Superuser created successfully")


if __name__ == "__main__":
    username: str = input("Enter username")
    email: str = input("Enter email")
    password: str = input("Enter password")

    create_superuser_cli(
        username=username,
        email=email,
        password=password
    )
