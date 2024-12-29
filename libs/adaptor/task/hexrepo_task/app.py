from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel
import logging

from .interface import TaskAdapter

logger = logging.getLogger(__name__)


TaskHandlerFuncType = Callable[..., Any]


class TaskCreateDTO(BaseModel):
    status: str
    name: str
    event: Dict[Any]
    created_at: datetime
    updated_at: datetime
    error: Optional[Dict[Any]]


class TaskDTO(TaskCreateDTO):
    id: UUID


class TaskUpdateDTO(BaseModel):
    status: Optional[str] = None
    error: Optional[Dict[Any]] = None


class TaskEvent(BaseModel):
    task_name: str
    task_id: Optional[UUID] = None
    event: Optional[Dict[Any]] = None
    

class Task:
    task_registry = {}

    def __init__(self, event: TaskEvent, task_adapter: TaskAdapter, uow: UOW):
        self.func: Callable = self.task_registry[event.task_name]
        self.event: TaskEvent = event
        self.uow: UOW = uow
        self.state: Optional[TaskDTO] = None
        if event.task_id:
            self.get_task_data()

    @classmethod
    def add_task_func(cls, func: Callable):
        func_name = func.__name__
        if cls.task_registry.get(func_name) and cls.tasks_registry.get(func_name) is not func:
            raise RuntimeError(f"Duplicate functions with name: {func_name} please rename: {func}")
        cls.task_registry[func_name] = func

    def get_task_data(self):
        self.state = self.uow.task.read(self.event.task_id)

    def update(self, **kwargs):
        # validate kwargs
        # self.state.update
        self.uow.task.update(self.event.task_id, kwargs)

    def queue(self):
        # Send task to queue
        self.state = self.uow.task.create(TaskCreateDTO(
            status="pending",
            name=self.event.task_name,
            event=self.event.event,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ))

    def execute(self):
        # Create task instance + state
        self.state = self.update(self.state.id, status="running")

        try:
            logger.info(f"Running task: {self.state.name}, id: {self.state.id}")
            self.func(self.event)
        except Exception as e:
            logger.error(f"Error running task: {self.name}, id: {self.id}, error: {e}")
            self.state = self.update(self.state.id, status="error", error=e)

        # Update Task status
        self.state = self.update(self.state.id, status="completed")


# Logic to run tasks from any queue provider
class TaskApp():
    def __init__(self, task_adapter: TaskAdapter, uow: UOW):
        self.task_adapter = task_adapter
        self.uow = uow
    
    def task(self):
        """Task decorator to register task functions"""
        def register_task(func: TaskHandlerFuncType) -> TaskHandlerFuncType:
            Task.add_task_func(func)
            return func
        
        return register_task
    
    def _get_task(self, event: TaskEvent) -> Task:
        """Get task by name"""
        task = Task(event)
        
        return task
    
    def queue_task(self, task: str | Callable, args: Dict[Any]) -> Task:
        """Call task by name"""
        if isinstance(task, callable):
            task = task.__name__
        event: TaskEvent = TaskEvent(task_name=task, event=args)
        task_instance: Task = Task(event, task_adapter=self.task_adapter, uow=self.uow)
        task_instance.queue()
        return task_instance
    
    def _parse_event(self, event: Dict[Any]) -> TaskEvent:
        """Parse event data"""
        return TaskEvent(**event)

    def handle(self, event: Dict[Any]):
        """Handle event and run task"""
        event: TaskEvent = self._parse_event(event)
        # parse event + create task instnace
        task: Task = self._get_task(event)
        # Execute task
        try:
            task.execute()
        except Exception as e:
            logger.error(f"Error running task: {task.name}, id: {task.id}, error: {e}")
            raise
    

app = TaskApp()

@app.task
def task_example(event):
    print(event)

app.queue("task_example", {"name": "example", "status": "running"})