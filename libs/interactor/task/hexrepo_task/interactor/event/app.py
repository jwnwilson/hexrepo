import inspect
import json
import logging
from asyncio import sleep
from contextlib import contextmanager
from functools import wraps
from inspect import signature
import types
from typing import Any, Callable, Dict, Generator, List, Optional, cast
from uuid import UUID

from fastapi.params import Depends
from pydantic import BaseModel

from hexrepo_task.exception import DuplicateTaskName, TaskNotFound

from ...config import TaskConfig
from ...config import config as default_config
from ...interface import QueueAdaptor, TaskCreateDTO, TaskDTO, TaskUpdateDTO
from ...interface import TaskUOW as UOW

logger = logging.getLogger(__name__)


TaskFunc = Callable[..., Any]
GetQueue = Callable[[], QueueAdaptor]
GetUOW = Callable[[], UOW]


class TaskApp:
    # Initialise task app to configure how tasks are run
    task_registry: Dict[str, Callable] = {}
    _dependency_overrides: Dict[Callable, Callable] = {}

    def __init__(
        self, get_queue: GetQueue, get_uow: GetUOW, config: Optional[TaskConfig] = None
    ):
        self._get_queue: GetQueue = get_queue
        self._get_uow: GetUOW = get_uow
        self.config: TaskConfig = config or default_config

    @property
    def dependency_overrides(self) -> Dict[Callable, Callable]:
        return self.__class__._dependency_overrides

    @dependency_overrides.setter
    def dependency_overrides(self, value: Dict[Callable, Callable]):
        self.__class__._dependency_overrides = value

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
        return TaskFuncWrapper(
            func, self, dependency_overrides=self.dependency_overrides
        )

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

    def queue_task(
        self, func: TaskFunc | "TaskFuncWrapper", params: Dict
    ) -> "TaskPromise":
        """Queue task from app initialising deodependencies"""
        if isinstance(func, TaskFuncWrapper):
            func = func.func
        # Check name is right even with wrapper
        func_name = func if isinstance(func, str) else func.__name__
        # Validate params
        self._validate_params(func, params)
        with self.get_queue() as queue, self.get_uow() as uow:
            try:
                task_adaptor: TaskAdaptor = self._get_task_adaptor(uow, queue)
                return task_adaptor.queue(func, params)
            except Exception as e:
                logger.error(
                    f"Error queueing task: {func_name}, param: {params}, error: {e}"
                )
                raise

    def _validate_params(self, func: TaskFunc, params: Dict):
        func_signature = signature(func)
        func_name: str = func.__name__
        for name, param in func_signature.parameters.items():
            if name not in params:
                if param.default == inspect.Parameter.empty:
                    raise ValueError(
                        f"Missing required parameter: {name} for task: {func_name}"
                    )
            is_dependency = isinstance(param.default, Dependency) or (
                hasattr(param.default, "__class__")
                and param.default.__class__.__name__ == "Depends"
            )
            if not is_dependency and not isinstance(params[name], param.annotation):
                raise ValueError(
                    f"Invalid type for parameter: {name} for task: {func_name}"
                )

    def _get_task_adaptor(self, uow: UOW, queue: QueueAdaptor) -> "TaskAdaptor":
        """Get task by name"""
        return TaskAdaptor(app=self, uow=uow, queue=queue, config=self.config)

    def _parse_event(self, event: Dict) -> TaskDTO:
        """Parse event data"""
        try:
            assert (
                len(event["Records"]) == 1
            ), "Expected 1 event, multiple are not handled"
            return TaskDTO(**json.loads(event["Records"][0]["body"]))
        except Exception as e:
            logger.error(f"Error parsing event: {event}, error: {e}")
            raise


class TaskAdaptor:
    """
    Task Adaptor to handle task data and queue operations
    """

    def __init__(
        self,
        app: TaskApp,
        uow: UOW,
        queue: QueueAdaptor,
        config: Optional[TaskConfig] = None,
    ):
        self._app: TaskApp = app
        self._uow: UOW = uow
        self._queue: QueueAdaptor = queue
        self._config: TaskConfig = config or default_config

    def _validate_task(self, task: TaskDTO | TaskCreateDTO):
        if task.name not in self._app.task_registry:
            raise TaskNotFound(f"Task not found: {task.name}")

    def read(self, id: UUID) -> TaskDTO:
        return self._uow.task.read(id)

    def update(self, id: UUID, task: TaskUpdateDTO) -> TaskDTO:
        # validate kwargs
        return self._uow.task.update(id, task)

    def _serialize_params(self, params: Dict) -> Dict:
        return {
            k: json.loads(v.model_dump_json()) if isinstance(v, BaseModel) else v
            for k, v in params.items()
        }

    def queue(self, func: TaskFunc, params: Dict[str, Any]) -> "TaskPromise":
        # Send task to queue
        func_name: str = func.__name__
        task_data: TaskCreateDTO = TaskCreateDTO(
            name=func_name, params=self._serialize_params(params)
        )
        self._validate_task(task_data)
        # Validate task param and error if invalid types
        task: TaskDTO = self._uow.task.create(task_data)
        try:
            logger.info(f"Queueing task: {task.name}, id: {task.id}")
            task = self._queue.add_task(task)
            if not task.task_id:
                raise Exception(f"Task not queued, missing task_id for task: {task}")
        except Exception as e:
            logger.error(f"Error queueing task: {task.name}, id: {task.id}, error: {e}")
            self.update(task.id, TaskUpdateDTO(status="error", error=str(e)))
            raise
        task = self.update(
            task.id, TaskUpdateDTO(status="queued", task_id=task.task_id)
        )
        return TaskPromise(task, task_adaptor=self)

    def execute(self, task: TaskDTO) -> Any:
        # Create task instance + state
        self._validate_task(task)
        task = self.update(task.id, TaskUpdateDTO(status="running"))
        func: TaskFunc = self._app.task_registry[task.name]
        try:
            logger.info(f"Running task: {task.name}, id: {task.id}")
            task_wrapper: TaskFuncWrapper = TaskFuncWrapper(
                func, self, dependency_overrides=self._app.dependency_overrides
            )
            result: Any = task_wrapper(**task.params)
        except Exception as e:
            logger.error(f"Error running task: {task.name}, id: {task.id}, error: {e}")
            self.update(task.id, TaskUpdateDTO(status="error", error=str(e)))
            raise

        # Update Task status
        self.state = self.update(task.id, TaskUpdateDTO(status="completed"))

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
    cache: Dict[Callable, Any] = {}

    def __init__(self, func: Callable, use_cache: bool = True, top_level: bool = True):
        self.func = func
        self.use_cache: bool = use_cache
        self.generator: Optional[Generator] = None
        self.top_level: bool = top_level

    def cleanup(self):
        if self.generator and self.top_level:
            try:
                next(self.generator)
            except StopIteration:
                pass

    def __call__(self) -> Any:
        if self.func in Dependency.cache:
            return Dependency.cache[self.func]

        result = self.func()
        if type(result) is types.GeneratorType:
            self.generator = result
            result = next(result)
        if self.use_cache:
            Dependency.cache[self.func] = result
        return result


def resolve_dependencies(func: Callable, top_level: bool = True, overrides: Optional[Dict[Callable, Callable]] = None) -> Callable:
    """Run functions with dependencies and resolve them.
    E.G.:

    @resolve_dependencies
    def my_func(id:str, get_uow: Dependency = Dependency(get_uow)) -> Any:
        return get_uow.user.read(id)

    OR

    resolve_dependencies(my_func)(id)

    top_level: Used to cleanup dependencies after function is run, avoids clean up in nested functions
    overrides: Used to replace dependencies during testing
    """
    f_sig = inspect.signature(func)
    overrides = overrides or {}
    def load_overrides(dep: Dependency | Depends) -> None:
        # replace dependency with override for testing if needed
        if type(dep) is Dependency:
            if dep.func in overrides:
                dep.func = overrides[dep.func]
        elif type(dep) is Depends:
            if dep.dependency in overrides:
                dep.dependency = overrides[dep.dependency]

    @wraps(func)
    def resolve_depends(*arg, **kwargs):
        bound = f_sig.bind(*arg, **kwargs)
        bound.apply_defaults()
        dependencies: List[Dependency] = []

        # resolve dependency function args and parse dicts into pydantic models
        for key, arg_v in bound.arguments.items():
            load_overrides(arg_v)
            if type(arg_v) is Dependency:
                dependencies.append(arg_v)
                bound.arguments[key] = resolve_dependencies(
                    arg_v, top_level=False, overrides=overrides
                )()
            elif type(arg_v) is Depends:
                dependencies.append(arg_v.dependency)
                bound.arguments[key] = resolve_dependencies(
                    arg_v.dependency, top_level=False, overrides=overrides
                )()
            # parse pydantic models
            elif BaseModel in inspect.getmro(
                f_sig.parameters[key].annotation
            ) and isinstance(arg_v, dict):
                bound.arguments[key] = f_sig.parameters[key].annotation(**arg_v)

        result = func(*bound.args, **bound.kwargs)

        if top_level:
            for dep in dependencies:
                if isinstance(dep, Dependency):
                    dep.cleanup()
                elif isinstance(dep, Generator):
                    try:
                        next(dep)
                    except StopIteration:
                        pass

        return result

    return resolve_depends


class TaskFuncWrapper:
    """
    Call task function and handle dependencies
    """

    def __init__(
        self, func: TaskFunc, app: TaskApp, dependency_overrides: Optional[Dict] = None
    ):
        self.app: TaskApp = app
        self.func: TaskFunc = func
        self.dependency_overrides: Dict = dependency_overrides or {}

    @property
    def __name__(self) -> str:
        return self.func.__name__
    
    def __call__(self, *args, **kwargs) -> Any:
        resolved_func = resolve_dependencies(self.func, overrides=self.dependency_overrides)
        return resolved_func(*args, **kwargs)

    def queue_task(self, **kwargs) -> TaskPromise:
        return self.app.queue_task(self.func, kwargs)
