import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from hexrepo_db.interface import UOW
from hexrepo_task.adaptor.db.nosql.uow import QueueUOW
from hexrepo_task.adaptor.queue import SqsQueueAdaptor
from hexrepo_task.app import TaskAdaptor, TaskApp
from hexrepo_task.interface import QueueAdaptor, QueueConfig

from app.adaptor.db.sql.uow import SqlUOW
from app.domain.example import ExampleDTO

# Silence SQLALchemy deprecation warning until we can upgrade
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"

# Create local file db
SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"


@pytest.fixture
def uow() -> Generator[UOW, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    uow = SqlUOW(db_url=SQLALCHEMY_DATABASE_URL)
    # Create DB session
    with uow.transaction():
        yield uow


@pytest.fixture(scope="function", autouse=True)
def create_tables(uow: UOW):
    uow.drop_all()
    uow.create_all()


@pytest.fixture
def client(uow, task_adaptor) -> TestClient:
    from app.interactor.api.fastapi import app
    from app.interactor.dependencies import get_task_adaptor, get_uow

    def get_uow_override():
        yield uow

    def get_task_adaptor_override():
        yield task_adaptor

    app.dependency_overrides[get_uow] = get_uow_override
    app.dependency_overrides[get_task_adaptor] = get_task_adaptor_override
    return TestClient(app)

@pytest.fixture
def example_data():
    return {
        "name": "test",
        "url": "https://test.com",
        "location": "test location",
    }


@pytest.fixture
def created_example(client: TestClient, example_data) -> ExampleDTO:
    response = client.post("/api/v1/example/", json=example_data)
    return ExampleDTO(**response.json())


@pytest.fixture
def queue() -> Generator[QueueAdaptor, None, None]:
    """
    Return a queue object.
    """
    config: QueueConfig = QueueConfig(
        default_queue="hexrepo-tasks",
        endpoint_url="http://localhost.localstack.cloud:4566",
    )
    queue_adapater: SqsQueueAdaptor = SqsQueueAdaptor(config=config)
    try:
        queue_adapater.delete_queue("hexrepo-tasks")
    except:
        pass
    queue_adapater.create_queue("hexrepo-tasks")
    return queue_adapater


@pytest.fixture
def queue_uow() -> Generator[UOW, None, None]:
    """
    Return db adaptor with initialised DB & DB session.
    """
    uow = QueueUOW(db_url="http://localhost.localstack.cloud:4566")
    # Create DB session
    yield uow


@pytest.fixture
def task_client(queue_uow, queue, uow) -> TestClient:
    from app.interactor.dependencies import get_uow

    def get_queue_uow_override():
        yield queue_uow

    def get_queue_override():
        yield queue

    def get_uow_override():
        yield uow
    
    # Make dependencies generic
    app: TaskApp = TaskApp(get_uow=get_queue_uow_override, get_queue=get_queue_override) 
    app.dependency_overrides[get_uow] = get_uow_override
    return app


@pytest.fixture()
def task_adaptor(
    task_client: TaskApp, queue: QueueAdaptor, queue_uow: UOW, uow: UOW
) -> Generator[QueueAdaptor, None, None]:
    
    task_adaptor = TaskAdaptor(task_client, uow=queue_uow, queue=queue)
    yield task_adaptor


@pytest.fixture(scope="function", autouse=True)
def create_tables_queue_uow(queue_uow: UOW):
    queue_uow.drop_all()
    queue_uow.create_all()
