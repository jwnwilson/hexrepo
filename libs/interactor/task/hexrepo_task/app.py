import logging
from asyncio import sleep
from datetime import datetime
from typing import Any, Callable, Dict, Optional, cast

from hexrepo_task.exception import DuplicateTaskName

from .config import TaskConfig
from .config import config as default_config
from .interface import QueueAdapter, TaskDTO, TaskUpdateDTO
from .interface import TaskUOW as UOW

logger = logging.getLogger(__name__)


TaskFunc = Callable[[TaskDTO], Any]
GetQueue = Callable[[], QueueAdapter]
GetUOW = Callable[[], UOW]

# Logic to run tasks from any queue provider
class TaskApp:
    def __init__(self, get_queue: GetQueue, get_uow: GetUOW):
        self.get_queue: GetQueue = get_queue
        self._queue: Optional[QueueAdapter] = None
        self.get_uow: GetUOW = get_uow
        self._uow: Optional[UOW] = None

    @property
    def queue(self) -> QueueAdapter:
        if self._queue is None:
            self._queue = self.get_queue()
        return self._queue
    
    @property
    def uow(self) -> UOW:
        if self._uow is None:
            self._uow = self.get_uow()
        return self._uow

    def task(self, func: TaskFunc, **config) -> "TaskFunc":
        """Task decorator to register task functions"""
        Task.add_task_func(func)

        task_config: TaskConfig = TaskConfig(**config)
        return TaskFuncWrapper(func, self, config=task_config)

    def handle(self, event: Dict | TaskDTO) -> Any:
        """Handle event and run task"""
        if isinstance(event, dict):
            event = self._parse_event(event)
        event = cast(TaskDTO, event)
        # parse event + create task instnace
        task: Task = self._get_task(event)
        # Execute task
        try:
            return task.execute()
        except Exception as e:
            logger.error(
                f"Error running task: {task.state.name}, id: {task.state.id}, error: {e}"
            )
            raise

    def _get_task(self, event: TaskDTO) -> "Task":
        """Get task by name"""
        task = Task(event, task_app=self)

        return task

    def _parse_event(self, event: Dict) -> TaskDTO:
        """Parse event data"""
        return TaskDTO(**event)


class Task:
    """
    Contain task data and manage metadata for a task function call
    """
    task_registry = {}

    def __init__(
        self, task: TaskDTO, task_app: TaskApp, config: Optional[TaskConfig] = None
    ):
        self.func: TaskFunc = self.task_registry[task.name]
        # self.event: TaskDTO = event
        self.app: TaskApp = task_app
        self.state: TaskDTO = task
        self.config: TaskConfig = config or default_config
        if task.id:
            self.refresh_task_data()

    @classmethod
    def add_task_func(cls, func: TaskFunc):
        func_name = func.__name__
        if (
            cls.task_registry.get(func_name)
            and cls.task_registry.get(func_name) is not func
        ):
            raise DuplicateTaskName(
                f"Duplicate functions with name: {func_name} please rename: {func}"
            )
        cls.task_registry[func_name] = func

    def refresh_task_data(self):
        self.state = self.app.uow.task.read(self.state.id)

    def update(self, **kwargs) -> TaskDTO:
        # validate kwargs
        task_param: TaskUpdateDTO = TaskUpdateDTO(**kwargs)
        return self.app.uow.task.update(self.state.id, task_param)

    def queue(self) -> "TaskPromise":
        # Send task to queue
        self.state = self.app.uow.task.create(
            TaskDTO(
                status="pending",
                name=self.state.name,
                params=self.state.params,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        )
        task_event = self.app.queue.add_task(self.state)
        if task_event.task_id:
            self.state = self.update(status="queued")
        return TaskPromise(self)

    def execute(self) -> Any:
        # Create task instance + state
        self.state = self.update(status="running")

        try:
            logger.info(f"Running task: {self.state.name}, id: {self.state.id}")
            task_wrapper: TaskFuncWrapper = TaskFuncWrapper(self.func, self.app, self.config) 
            result: Any = task_wrapper(self.state)
        except Exception as e:
            logger.error(
                f"Error running task: {self.state.name}, id: {self.state.id}, error: {e}"
            )
            self.state = self.update(status="error", error=str(e))
            raise

        # Update Task status
        self.state = self.update(status="completed")

        return result


class TaskPromise:
    def __init__(self, task: "Task", timeout: int = 30):
        self.task: Task = task
        self.timeout: int = timeout

    def wait(self):
        """Wait for task to complete"""
        timer: int = 0
        self.task.refresh_task_data()
        while self.task.state.status not in ["completed", "error"]:
            if timer >= self.timeout:
                raise TimeoutError(
                    f"Task took too long to complete: {self.task.state.name}, id: {self.task.state.id}"
                )
            sleep(1)
            timer += 1
            self.task.refresh_task_data()
        return self.task.state
    

class Dependency:
    def __init__(self, get_dependency: Callable):
        self.get_dependency = get_dependency

    def __get__(self, obj, objtype):
        return self.get_dependency()


class TaskFuncWrapper:
    """
    Call task function and handle dependencies
    """
    def __init__(
        self, func: TaskFunc, task_app: TaskApp, config: Optional[TaskConfig] = None
    ):
        Task.add_task_func(func)

        self.func: TaskFunc = func
        self.app: TaskApp = task_app
        self.config: Optional[TaskConfig] = config or default_config

    def _get_dependencies(self, func: TaskFunc) -> Dict:
        dependencies = {}
        for name, param in func.__annotations__.items():
            name: str
            param: Any
            if isinstance(param, Dependency):
                dependencies[name] = param.get_dependency()
        return dependencies

    def queue(self, params: Optional[Dict] = None) -> TaskPromise:
        task = TaskDTO(name=self.func.__name__, params=params)
        return Task(task, self.app).queue()

    def __call__(self, task: TaskDTO):
        dependencies = self._get_dependencies(self.func)
        return self.func(task, **dependencies)


# if __name__ == "__main__":

#     def get_queue() -> QueueAdapter:
#         return SqsQueueAdapter(queue="hexrepo-tasks")
#     def get_uow() -> UOW:
#         return DynamoUOW()
    
#     app = TaskApp(uow=get_uow(), queue=get_queue())

#     @app.task
#     def task_A(event: TaskDTO):
#         print(event)

#     @app.task
#     def task_B(event: TaskDTO):
#         print(event)

#     # run task directly
#     task_result = task_A(params=dict(name="example", status="running"))

#     # queue task
#     task_queue_instance: TaskPromise = task_A.queue()

#     # Using generator will require server instead of being serverless
#     # need to do this but keep it serverless
#     # Might need to have a long running async lambda process to manage these tasks
#     @app.flow
#     async def workflow_a(*args, **kwargs):
#         try:
#             queue: TaskPromise = task_A.queue(*args, **kwargs)
#             results = queue.wait()

#             concurrent = []
#             for res in results:
#                 concurrent.append(task_B.queue(res))
#                 concurrent.append(task_C.queue(res))

#             all(c.wait() for c in concurrent)
#         except:
#             error_logic()

#     workflow_a.trigger()
