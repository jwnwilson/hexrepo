from .tasks.app import app


def handler(event, context):
    return app.handle(event)
