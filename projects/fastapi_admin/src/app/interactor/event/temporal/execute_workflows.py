from temporalio.client import Client

from .workflows import (
    IngestionWorkflow,
    ProcessFileInput,
    ProcessFileResult,
    ProcessFileWorkflow,
)


async def execute_demo(file_path: str) -> ProcessFileResult:
    client: Client = await Client.connect("localhost:7233")

    result: ProcessFileResult = await client.execute_workflow(
        ProcessFileWorkflow.run,
        ProcessFileInput(file_path=file_path, chunk_size=100_000),
        id="wallet_address_ingestion",
        task_queue="file-processing-queue",
    )
    return result


async def execute_file_ingestion(file_path: str, batch_size: int) -> ProcessFileResult:
    client: Client = await Client.connect("localhost:7233")

    result: ProcessFileResult = await client.execute_workflow(
        IngestionWorkflow.run,
        ProcessFileInput(file_path=file_path, chunk_size=batch_size),
        id="data_ingestion",
        task_queue="file-processing-queue",
    )
    return result
