from hexrepo_task.interactor.event.app import resolve_dependencies

from app.domain.user import UserCreateDTO, UserManager, UserPermissionDTO
from app.interactor.dependencies import get_user_manager


@resolve_dependencies
def create_superuser_cli(
    username: str, email: str, password: str, name:str, user_manager: UserManager = get_user_manager()
):
    """
    Create superuser CLI
    """
    print("Creating superuser...")
    # Need a way to use dependencies outside fastapi
    user_dto: UserPermissionDTO = user_manager.create_user(
        UserCreateDTO(
            username=username,
            password=password,
            email=email,
            name=name
        ),
        superuser=True
    )

    print(f"Superuser {user_dto.username} created successfully")


if __name__ == "__main__":
    username: str = input("Enter username")
    email: str = input("Enter email")
    password: str = input("Enter password")

    create_superuser_cli(username=username, email=email, password=password)
