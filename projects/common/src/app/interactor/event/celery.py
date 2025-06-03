from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')


@app.task
def add(x, y):
    return x + y


from hexrepo_task.interactor.event.app import Dependency, TaskApp, TaskDTO

from app.adaptor.db.sql import SqlUOW
from app.domain.user import UserPermissionCreateDTO

from ...dependencies import get_queue_uow, get_task_queue, get_uow

# mode lambda / celery
app = TaskApp(mode="celery", get_uow=get_queue_uow, get_queue=get_task_queue)


# in celery mode return a celery task
@app.task
def create_example_task(task: TaskDTO, uow: SqlUOW = Dependency(get_uow)):
    user_dto: UserPermissionCreateDTO = UserPermissionCreateDTO(**task.params)
    uow.user.create(user_dto)
