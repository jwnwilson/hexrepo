from app.adaptor.db.interface import UOW
from app.interactor.dependencies import get_uow


def create_superuser_cli():
    """
    Create superuser CLI
    """
    # Need a way to use dependencies outside fastapi
    uow: UOW = get_uow()
    uow.create_superuser()
    print("Superuser created successfully")


if __name__ == "__main__":
    create_superuser_cli()
