from datetime import datetime
from typing import Any, Callable, Dict, Optional
from uuid import UUID
from pydantic import BaseModel
import logging

from .interface import QueueAdapter, TaskCreateDTO, TaskDTO, TaskUOW as UOW, TaskUpdateDTO
from .config import TaskConfig, config as default_config
from .adaptor.db.nosql import DynamoUOW
from .adaptor.queue import SqsQueueAdapter

logger = logging.getLogger(__name__)


TaskHandlerFuncType = Callable[..., Any]


    

# Logic to run tasks from any queue provider
class TaskApp():
    def __init__(self, queue: QueueAdapter, uow: UOW):
        self.queue: QueueAdapter = queue
        self.uow: UOW = uow
    
    def task(self, func: Callable, *args, **kwargs) -> "TaskFunc":
        """Task decorator to register task functions"""
        Task.add_task_func(func)
        
        return TaskFunc(func, self, *args, **kwargs)
    
    # def queue(self, task: str | Callable, args: Dict[Any]) -> Task:
    #     """Call task by name"""
    #     if isinstance(task, callable):
    #         task = task.__name__
    #     event: TaskDTO = TaskDTO(task_name=task, args=args)
    #     task_instance: Task = Task(event, task_adapter=self.task_adapter, uow=self.uow)
    #     task_instance.queue()
    #     return task_instance
    
    def handle(self, event: Dict[Any]):
        """Handle event and run task"""
        event: TaskDTO = self._parse_event(event)
        # parse event + create task instnace
        task: Task = self._get_task(event)
        # Execute task
        try:
            task.execute()
        except Exception as e:
            logger.error(f"Error running task: {task.state.name}, id: {task.state.id}, error: {e}")
            raise
    
    def _get_task(self, event: TaskDTO) -> "Task":
        """Get task by name"""
        task = Task(event, task_app=self)
        
        return task
    
    def _parse_event(self, event: Dict[Any]) -> TaskDTO:
        """Parse event data"""
        return TaskDTO(**event)
    

class Task:
    task_registry = {}

    def __init__(self, event: TaskDTO, task_app: TaskApp, config: Optional[TaskConfig] = None):
        self.func: Callable = self.task_registry[event.name]
        self.event: TaskDTO = event
        self.app: TaskApp = task_app
        self.state: Optional[TaskDTO] = None
        self.config: Optional[TaskConfig] = config or default_config
        if event.task_id:
            self.refresh_task_data()
    
    @classmethod
    def add_task_func(cls, func: Callable):
        func_name = func.__name__
        if cls.task_registry.get(func_name) and cls.task_registry.get(func_name) is not func:
            raise RuntimeError(f"Duplicate functions with name: {func_name} please rename: {func}")
        cls.task_registry[func_name] = func

    def refresh_task_data(self):
        self.state = self.app.uow.task.read(self.state.id)

    def update(self, **kwargs) -> TaskDTO:
        # validate kwargs
        task_param: TaskUpdateDTO = TaskUpdateDTO(**kwargs)
        return self.app.uow.task.update(self.state.id, task_param)

    def queue(self):
        # Send task to queue
        self.state = self.app.uow.task.create(TaskCreateDTO(
            status="pending",
            name=self.event.name,
            params=self.event.params,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ))
        task_event = self.app.queue.add_task(self.state)
        if task_event.task_id:
            self.state = self.update(status="queued")

    def execute(self):
        # Create task instance + state
        self.state = self.update(self.state.id, status="running")

        try:
            logger.info(f"Running task: {self.state.name}, id: {self.state.id}")
            self.func(self.state.event)
        except Exception as e:
            logger.error(f"Error running task: {self.state.name}, id: {self.state.id}, error: {e}")
            self.state = self.update(self.state.id, status="error", error=e)

        # Update Task status
        self.state = self.update(self.state.id, status="completed")


class TaskFunc(object):
    
    def __init__(self, func: Callable, task_app: TaskApp, args: Dict[Any], kwargs: Dict[Any]):
        Task.add_task_func(func)

        self.func: Callable = func
        self.app: TaskApp = task_app
        self.args: Dict[Any] = args
        self.kwargs: Dict[Any] = kwargs
    
    def queue(self, **kwargs) -> Task:
        event = TaskDTO(task_name=self.func.__name__, args=kwargs)
        return Task(event, self.app).queue()

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)
    

if __name__ == "__main__":
    app = TaskApp(uow=DynamoUOW(), queue=SqsQueueAdapter())

    @app.task
    def task_A(event: TaskDTO):
        print(event)

    @app.task
    def task_B(event: TaskDTO):
        print(event)

    # run task directly
    task_result = task_A(name="example", status="running")

    # queue task
    task_queue_instance = task_A.queue()

    # Using generator will require server instead of being serverless
    # need to do this but keep it serverless
    # Might need to have a long running async lambda process to manage these tasks
    @app.flow
    async def workflow_a(*args, **kwargs):
        try:
            queue = task_A.queue(*args, **kwargs)
            results = queue.wait()

            concurrent = []
            for res in results:
                concurrent.append(task_B.queue(res))
                concurrent.append(task_C.queue(res))
            
            all(c.wait() for c in concurrent)
        except:
            error_logic()

    workflow_a.trigger()

    