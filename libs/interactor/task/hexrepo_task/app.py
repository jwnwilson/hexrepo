from contextlib import contextmanager
import inspect
import logging
from asyncio import sleep
from datetime import datetime
from typing import Any, Callable, Dict, Generator, Optional, cast

from hexrepo_task.exception import DuplicateTaskName

from .config import TaskConfig
from .config import config as default_config
from .interface import QueueAdapter, TaskDTO, TaskUpdateDTO
from .interface import TaskUOW as UOW

logger = logging.getLogger(__name__)


TaskFunc = Callable[[TaskDTO], Any]
GetQueue = Callable[[], QueueAdapter]
GetUOW = Callable[[], UOW]


class TaskApp:
    # Initialise task app to configure how tasks are run
    task_registry: Dict[str, Callable] = {}

    def __init__(self, get_queue: GetQueue, get_uow: GetUOW):
        self._get_queue: GetQueue = get_queue
        self._get_uow: GetUOW = get_uow

    @contextmanager
    def get_queue(self) -> Generator[QueueAdapter, None, None]:
        queue = self._get_queue()
        if isinstance(queue, Generator):
            yield queue
            next(queue)
        else:
            return queue
        
    @contextmanager
    def get_uow(self) -> Generator[UOW, None, None]:
        uow = self._get_uow()
        if isinstance(uow, Generator):
            yield uow
            next(uow)
        else:
            return uow
    
    def add_task_func(self, func: TaskFunc):
        func_name = func.__name__
        if (
            self.task_registry.get(func_name)
            and self.task_registry.get(func_name) is not func
        ):
            raise DuplicateTaskName(
                f"Duplicate functions with name: {func_name} please rename: {func}"
            )
        self.task_registry[func_name] = func

    def task(self, func: TaskFunc, **config) -> "TaskFuncWrapper":
        """Task decorator to register task functions"""
        self.add_task_func(func)

        task_config: TaskConfig = TaskConfig(**config)
        return TaskFuncWrapper(func, self, config=task_config)

    def handle(self, event: Dict | TaskDTO) -> Any:
        """Handle event and run task"""
        if isinstance(event, dict):
            event = self._parse_event(event)
        event = cast(TaskDTO, event)
        # parse event + create task instance
        with self.get_queue() as queue, self.get_uow() as uow:
            # Execute task
            try:
                task: Task = self._get_task(event, uow, queue)
                return task.execute()
            except Exception as e:
                logger.error(
                    f"Error running task: {task.state.name}, id: {task.state.id}, error: {e}"
                )
                raise

    def queue_task(self, func: TaskFunc, param: Dict) -> "TaskPromise":
        """Queue task"""
        event: TaskDTO = TaskDTO(name=func.__name__, params=param)
        with self.get_queue() as queue, self.get_uow() as uow:
            try:
                task: Task = self._get_task(event, uow, queue)
                return task.queue_task()
            except Exception as e:
                logger.error(
                    f"Error queueing task: {task.state.name}, id: {task.state.id}, error: {e}"
                )
                raise

    def _get_task(self, event: TaskDTO, uow: UOW, queue: QueueAdapter) -> "Task":
        """Get task by name"""
        task = Task(event, task_app=self, uow=uow, queue=queue)

        return task

    def _parse_event(self, event: Dict) -> TaskDTO:
        """Parse event data"""
        return TaskDTO(**event)


class Task:
    """
    Task instance to run task
    """
    def __init__(
        self, task: TaskDTO, app: TaskApp, uow:UOW, queue: QueueAdapter, config: Optional[TaskConfig] = None
    ):
        self.func: TaskFunc = app.task_registry[task.name]
        self.app: TaskApp = app
        self.uow: UOW = uow
        self.queue: QueueAdapter = queue
        self.state: TaskDTO = task
        self.config: TaskConfig = config or default_config
        if task.id:
            self.refresh_task_data()

    def refresh_task_data(self):
        self.state = self.uow.task.read(self.state.id)

    def update(self, **kwargs) -> TaskDTO:
        # validate kwargs
        task_param: TaskUpdateDTO = TaskUpdateDTO(**kwargs)
        return self.uow.task.update(self.state.id, task_param)

    def queue_task(self) -> "TaskPromise":
        # Send task to queue
        self.state = self.uow.task.create(
            TaskDTO(
                status="pending",
                name=self.state.name,
                params=self.state.params,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        )
        task_event = self.queue.add_task(self.state)
        if task_event.task_id:
            self.state = self.update(status="queued")
        return TaskPromise(self)

    def execute(self) -> Any:
        # Create task instance + state
        self.state = self.update(status="running")

        try:
            logger.info(f"Running task: {self.state.name}, id: {self.state.id}")
            task_wrapper: TaskFuncWrapper = TaskFuncWrapper(
                self.func, self.app, self.config
            )
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
        self._get_dependency = get_dependency

    def get_dependency(self) -> Generator:
        return self._get_dependency()


class TaskFuncWrapper:
    """
    Call task function and handle dependencies
    """

    def __init__(self, func: TaskFunc):
        self.func: TaskFunc = func

    @contextmanager
    def _get_dependencies(self, func: TaskFunc, kwargs: Dict) -> Generator[Dict, None, None]:
        dependencies = {}
        dependency_generators = {}
        for name, param in inspect.signature(func).parameters.items():
            name: str
            param: inspect.Parameter
            if name in kwargs:
                dependencies[name] = kwargs[name]
            elif isinstance(param.default, Dependency):
                dep_return = param.default.get_dependency()
                if isinstance(dep_return, Generator):
                    dependency_generators[name] = dep_return
                    dependencies[name] = yield dependency_generators[name]
                else:
                    dependencies[name] = dep_return
            else:
                dependencies[name] = param.default
        yield dependencies

        # Clean up dependence generators
        for dep in dependency_generators:
            next(dependency_generators[dep])

    def __call__(self, task: TaskDTO, **kwargs) -> Any:
        with self._get_dependencies(self.func, kwargs) as dependencies:
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
