from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4
from hexrepo_db.interface import UOW
from pydantic import BaseModel
import logging

from .interface import QueueAdapter, TaskAdapter

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
    args: Optional[Dict[Any]] = None
    

class Task:
    task_registry = {}

    def __init__(self, event: TaskEvent, queue_adaptor: QueueAdapter, uow: UOW):
        self.func: Callable = self.task_registry[event.task_name]
        self.event: TaskEvent = event
        self.uow: UOW = uow
        self.queue_adaptor: QueueAdapter = queue_adaptor
        self.state: Optional[TaskDTO] = None
        if event.task_id:
            self.get_task_data()

    @classmethod
    def add_task_func(cls, func: Callable):
        func_name = func.__name__
        if cls.task_registry.get(func_name) and cls.task_registry.get(func_name) is not func:
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
            event=self.event.args,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ))
        taskEvent = TaskEvent(task_id=self.state.id, task_name=self.state.name, args=self.event.args)
        queue_instance = self.queue_adaptor.add_task(taskEvent)
        if queue_instance:
            self.state = self.update(status="queued")

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


class TaskFunc(object):
    def __init__(self, func: Callable, queue_adaptor: QueueAdapter, uow: UOW, args: Dict[Any], kwargs: Dict[Any]):
        self.func: Callable = func
        self.queue_adaptor: QueueAdapter = queue_adaptor
        self.uow: UOW = uow
        self.args: Dict[Any] = args
        self.kwargs: Dict[Any] = kwargs
    
    def queue(self, **kwargs) -> Task:
        event = TaskEvent(task_name=self.func.__name__, args=kwargs)
        return Task(event, self.queue_adaptor, self.uow).queue()

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)
    

# Logic to run tasks from any queue provider
class TaskApp():
    def __init__(self, queue: QueueAdapter, uow: UOW):
        self.queue = queue
        self.uow = uow
    
    def task(self, func: Callable, *args, **kwargs) -> TaskFunc:
        """Task decorator to register task functions"""
        Task.add_task_func(func)
        
        return TaskFunc(func, self.queue, self.uow, *args, **kwargs)
    
    def _get_task(self, event: TaskEvent) -> Task:
        """Get task by name"""
        task = Task(event)
        
        return task
    
    def queue(self, task: str | Callable, args: Dict[Any]) -> Task:
        """Call task by name"""
        if isinstance(task, callable):
            task = task.__name__
        event: TaskEvent = TaskEvent(task_name=task, args=args)
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
            logger.error(f"Error running task: {task.state.name}, id: {task.state.id}, error: {e}")
            raise
    

if __name__ == "__main__":
    app = TaskApp(uow=UOW(), queue=QueueAdapter())

    @app.task
    def task_A(event: TaskEvent):
        print(event)

    @app.task
    def task_B(event: TaskEvent):
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

    