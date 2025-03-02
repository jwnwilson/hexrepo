from typing import Optional
from hexrepo_task.interactor.event.app import Dependency, resolve_dependencies

from app.domain.user import UserCreateDTO, UserManager, UserPermissionDTO
from app.interactor.dependencies import get_user_manager
from app.config import config


@resolve_dependencies
def create_user_cli(
    username: str,
    email: str,
    password: str,
    name: str,
    create_superuser: bool = False,
    user_manager: UserManager = Dependency(get_user_manager),
):
    """
    Create superuser CLI
    """
    print("Creating superuser...")
    # Need a way to use dependencies outside fastapi
    user_dto: UserPermissionDTO = user_manager.create_user(
        UserCreateDTO(username=username, password=password, email=email, name=name),
        superuser=create_superuser,
    )

    print(f"Superuser {user_dto.username} created successfully")


if __name__ == "__main__":
    # prompt for user details
    if not config.ENVIRONMENT:
        raise ValueError("Environment not set") 
    create_superuser: bool = input("Create superuser? (y/n)\n") == "y"
    username: str = input("Enter username:\n")
    name: str = input("Enter name:\n")
    email: str = input("Enter email:\n")
    password: str = input("Enter password:\n")

    create_user_cli(username=username, email=email, password=password, name=name, create_superuser=create_superuser)
