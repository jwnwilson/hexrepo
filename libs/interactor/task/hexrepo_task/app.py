from contextlib import contextmanager
import inspect
import logging
from asyncio import sleep
from datetime import datetime
from typing import Any, Callable, Dict, Generator, Optional, cast
from uuid import UUID

from hexrepo_task.exception import DuplicateTaskName, TaskNotFound

from .config import TaskConfig
from .config import config as default_config
from .interface import QueueAdaptor, TaskCreateDTO, TaskDTO, TaskUpdateDTO
from .interface import TaskUOW as UOW

logger = logging.getLogger(__name__)


TaskFunc = Callable[[TaskDTO], Any]
GetQueue = Callable[[], QueueAdaptor]
GetUOW = Callable[[], UOW]


class TaskApp:
    # Initialise task app to configure how tasks are run
    task_registry: Dict[str, Callable] = {}

    def __init__(self, get_queue: GetQueue, get_uow: GetUOW, config: Optional[TaskConfig] = None):
        self._get_queue: GetQueue = get_queue
        self._get_uow: GetUOW = get_uow
        self.config: TaskConfig = config or default_config

    @contextmanager
    def get_queue(self) -> Generator[QueueAdaptor, None, None]:
        queue = self._get_queue()
        if isinstance(queue, Generator):
            for _ in queue:
                yield _
        else:
            yield queue
        
    @contextmanager
    def get_uow(self) -> Generator[UOW, None, None]:
        uow = self._get_uow()
        if isinstance(uow, Generator):
            for _ in uow:
                yield _
        else:
            yield uow
    
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
        return TaskFuncWrapper(func)

    def handle(self, event: Dict | TaskDTO) -> Any:
        """Handle event and run task"""
        if isinstance(event, dict):
            event = self._parse_event(event)
        task: TaskDTO = cast(TaskDTO, event)
        # parse event + create task instance
        with self.get_queue() as queue, self.get_uow() as uow:
            # Execute task
            try:
                task_adaptor: TaskAdaptor = self._get_task_adaptor(uow, queue)
                return task_adaptor.execute(task)
            except Exception as e:
                logger.error(
                    f"Error running task: {event.name}, id: {event.id}, error: {e}"
                )
                raise

    def queue_task(self, func: str | TaskFunc, params: Dict) -> "TaskPromise":
        """Queue task from app initialising deodependencies"""
        # Check name is right even with wrapper
        func_name = func if isinstance(func, str) else func.__name__
        with self.get_queue() as queue, self.get_uow() as uow:
            try:
                task_adaptor: TaskAdaptor = self._get_task_adaptor(uow, queue)
                return task_adaptor.queue(func, params)
            except Exception as e:
                logger.error(
                    f"Error queueing task: {func_name}, param: {params}, error: {e}"
                )
                raise

    def _get_task_adaptor(self, uow: UOW, queue: QueueAdaptor) -> "TaskAdaptor":
        """Get task by name"""
        return TaskAdaptor(app=self, uow=uow, queue=queue, config=self.config)

    def _parse_event(self, event: Dict) -> TaskDTO:
        """Parse event data"""
        return TaskDTO(**event)


class TaskAdaptor:
    """
    Task Adaptor to handle task data and queue operations
    """
    def __init__(
        self, app: TaskApp, uow:UOW, queue: QueueAdaptor, config: Optional[TaskConfig] = None
    ):
        self._app: TaskApp = app
        self._uow: UOW = uow
        self._queue: QueueAdaptor = queue
        self._config: TaskConfig = config or default_config

    def _validate_task(self, task: TaskDTO | TaskCreateDTO):
        if not task.name in self._app.task_registry:
            raise TaskNotFound(f"Task not found: {task.name}")

    def read(self, id: UUID) -> TaskDTO:
        return self._uow.task.read(id)

    def update(self, id: UUID, task: TaskUpdateDTO) -> TaskDTO:
        # validate kwargs
        return self._uow.task.update(id, task)

    def queue(self, func: str | TaskFunc, params: Dict) -> "TaskPromise":
        # Send task to queue
        func_name: str = func if isinstance(func, str) else func.__name__
        task_data: TaskCreateDTO = TaskCreateDTO(name=func_name, params=params)
        self._validate_task(task_data)
        # Validate task param and error if invalid types
        task: TaskDTO = self._uow.task.create(task_data)
        try:
            logger.info(f"Queueing task: {task.name}, id: {task.id}")
            task = self._queue.add_task(task)
            if not task.task_id:
                raise Exception(f"Task not queued, missing task_id for task: {task}")
        except Exception as e:
            logger.error(
                f"Error queueing task: {task.name}, id: {task.id}, error: {e}"
            )
            self.update(task.id, TaskUpdateDTO(status="error", error=str(e)))
            raise
        task = self.update(task.id, TaskUpdateDTO(status="queued", task_id=task.task_id))
        return TaskPromise(task, task_adaptor=self)

    def execute(self, task: TaskDTO) -> Any:
        # Create task instance + state
        self._validate_task(task)
        task = self.update(task.id, TaskUpdateDTO(status="running"))
        func: TaskFunc = self._app.task_registry[task.name]
        try:
            logger.info(f"Running task: {task.name}, id: {task.id}")
            task_wrapper: TaskFuncWrapper = TaskFuncWrapper(
                func
            )
            result: Any = task_wrapper(task)
        except Exception as e:
            logger.error(
                f"Error running task: {task.name}, id: {task.id}, error: {e}"
            )
            self.update(task.id, TaskUpdateDTO(status="error", error=str(e)))
            raise

        # Update Task status
        self.state = self.update(task.id,TaskUpdateDTO(status="completed"))

        return result


class TaskPromise:
    def __init__(self, task: TaskDTO, task_adaptor: TaskAdaptor, timeout: int = 30):
        self.task: TaskDTO = task
        self.task_adaptor: TaskAdaptor = task_adaptor
        self.timeout: int = timeout

    def wait(self) -> None:
        """Wait for task to complete"""
        timer: int = 0
        self.task = self.task_adaptor.read(self.task.id)
        while self.task.status not in ["completed", "error"]:
            if timer >= self.timeout:
                raise TimeoutError(
                    f"Task took too long to complete: {self.task.state.name}, id: {self.task.state.id}"
                )
            sleep(1)
            timer += 1
            self.task_adaptor.read(self.task.id)
        return


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
        # validate func is compatible with task app error if invalid args
        self.func: TaskFunc = func

    @property
    def __name__(self) -> str:
        return self.func.__name__

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
                    dependencies[name] = next(dependency_generators[name])
                else:
                    dependencies[name] = dep_return
            else:
                dependencies[name] = param.default
        yield dependencies

        # Clean up dependence generators
        for dep in dependency_generators:
            try:
                next(dependency_generators[dep])
            except StopIteration:
                pass

    def __call__(self, task: TaskDTO, **kwargs) -> Any:
        task_kwargs: Dict = kwargs.copy()
        task_kwargs["task"] = task
        with self._get_dependencies(self.func, task_kwargs) as dependencies:
            return self.func(**dependencies)


# if __name__ == "__main__":

#     def get_queue() -> QueueAdaptor:
#         return SqsQueueAdaptor(queue="hexrepo-tasks")
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
#     task_result = task_A(param=dict(name="example", status="running"))

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
