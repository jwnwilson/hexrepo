from hexrepo_task.interactor.event.app import Dependency, resolve_dependencies

from app.domain.user import UserManager
from app.interactor.dependencies import get_user_manager


@resolve_dependencies
def create_default_permissions_cli(
    user_manager: UserManager = Dependency(get_user_manager),
):
    """
    Create default permissions CLI
    """
    print("Creating default permissions...")
    # Need a way to use dependencies outside fastapi
    user_manager.permission_manager.create_default_permissions()

    print("Create default permissions successfully")


if __name__ == "__main__":
    create_default_permissions_cli()
