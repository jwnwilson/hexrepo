from .tasks import task_app


def handler(event, context):
    return task_app.handle(event)
