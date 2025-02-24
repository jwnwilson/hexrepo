from app.adaptor.db.interface import UOW
from app.domain.user import UserPermissionCreateDTO
from app.interactor.dependencies import get_uow
from hexrepo_task.interactor.event.app import resolve_dependencies


@resolve_dependencies
def create_superuser_cli(uow: UOW = get_uow()):
    """
    Create superuser CLI
    """
    # Need a way to use dependencies outside fastapi
    uow.user.create(UserPermissionCreateDTO(
        username="jwnwilson",
        password="",
        email="jwnwilson@hotmail.co.uk"
    ))
    print("Superuser created successfully")


if __name__ == "__main__":
    create_superuser_cli()
