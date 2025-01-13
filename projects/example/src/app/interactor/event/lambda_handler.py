from hexrepo_log.log import setup_logger, log_manager
from .tasks import task_app


def handler(event, context):
    setup_logger()

    with log_manager():
        return task_app.handle(event)

