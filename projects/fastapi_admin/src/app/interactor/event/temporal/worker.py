import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activities import (
    convert_to_jsonl,
    get_chunk_offsets,
    index_records,
    load_wallet_data,
    map_pii_to_node_ids,
    validate_wallets,
)
from .workflows import IngestionWorkflow, ProcessFileWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="file-processing-queue",
        workflows=[ProcessFileWorkflow, IngestionWorkflow],
        activities=[
            get_chunk_offsets,
            validate_wallets,
            load_wallet_data,
            map_pii_to_node_ids,
            convert_to_jsonl,
            index_records,
        ],
        max_concurrent_activities=10,  # How many activities this worker runs at once
    )

    print("Worker started, polling for tasks...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
