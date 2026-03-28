import asyncio
from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from .activities import (
        ChunkResult,
        convert_to_jsonl,
        get_chunk_offsets,
        index_records,
        load_wallet_data,
        map_pii_to_node_ids,
        validate_wallets,
    )


@dataclass
class ProcessFileInput:
    file_path: str
    chunk_size: int = 1000


@dataclass
class ProcessFileResult:
    total_chunks: int
    total_records: int
    total_valid: int
    total_invalid: int


@workflow.defn
class ProcessFileWorkflow:
    @workflow.run
    async def run(self, input: ProcessFileInput) -> ProcessFileResult:
        # calulate all the chunk offsets to seek quickly
        offsets: list[list[int]] = await workflow.execute_activity(
            get_chunk_offsets,
            args=[input.file_path, input.chunk_size],
            start_to_close_timeout=timedelta(seconds=120),
        )

        workflow.logger.info(f"File split into {len(offsets)} chunks. Fanning out...")

        # DEMO NOTES: Fan out schedule ALL chunks concurrently ##
        # Each call to workflow.execute_activity() returns a coroutine.
        # Gather them all and asyncio.gather() waits for every single one.
        # Temporal schedules all of these as separate tasks on the task queue.
        # ### Look at the webUI ###
        # Workers pick them up and process as many as they can concurrently.
        tasks = [
            workflow.execute_activity(
                validate_wallets,
                args=[
                    input.file_path,
                    chunk_id,
                    offsets[chunk_id][0],
                    offsets[chunk_id][1],
                ],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            for chunk_id in range(len(offsets))
        ]

        # wait for all chunks to complete This is the fan in bit
        results: list[ChunkResult] = await asyncio.gather(*tasks)

        workflow.logger.info("All chunks processed. Loading data into db...")

        tasks = [
            workflow.execute_activity(
                load_wallet_data,
                args=[result.validated_filename],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            for result in results
        ]

        # wait for all chunks to complete This is the fan in bit
        await asyncio.gather(*tasks)

        workflow.logger.info("All chunks processed. Aggregating results...")

        # Aggregate
        return ProcessFileResult(
            total_chunks=len(results),
            total_records=sum(r.total for r in results),
            total_valid=sum(r.valid for r in results),
            total_invalid=sum(r.invalid for r in results),
        )


def flatten(xss):
    return [x for xs in xss for x in xs]


@workflow.defn
class IngestionWorkflow:
    @workflow.run
    async def run(self, input: ProcessFileInput) -> ProcessFileResult:
        # Convert files to jsonl is necessary
        jsonl_filepath: str = "./data/input/ingestion_data.jsonl"

        await workflow.execute_activity(
            convert_to_jsonl,
            args=[input.file_path, jsonl_filepath],
            start_to_close_timeout=timedelta(seconds=120),
        )

        # Break file to allow parallel mapping
        offsets: list[list[int]] = await workflow.execute_activity(
            get_chunk_offsets,
            args=[jsonl_filepath, input.chunk_size],
            start_to_close_timeout=timedelta(seconds=120),
        )

        workflow.logger.info(f"File split into {len(offsets)} chunks. Fanning out...")

        # Parallel store pii to node_id in map
        # Get map of current pii -> node_id store in memory
        tasks = [
            workflow.execute_activity(
                map_pii_to_node_ids,
                args=[
                    jsonl_filepath,
                    chunk_id,
                    offsets[chunk_id][0],
                    offsets[chunk_id][1],
                ],
                start_to_close_timeout=timedelta(seconds=300),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            for chunk_id in range(len(offsets))
            # Testing delete me:
            # for chunk_id in [0]
        ]

        # wait for all chunks to complete
        file_paths: list[list[str, str]] = await asyncio.gather(*tasks)

        workflow.logger.info(
            "Mapped pii to node_id combining and removing duplicates..."
        )

        # Combine data and remove duplicate nodes

        # Parallel add addresses to nodes_ids

        # Save in DB

        # Save in elasticsearch
        tasks = [
            workflow.execute_activity(
                index_records,
                args=[filepath],
                start_to_close_timeout=timedelta(seconds=300),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            for filepath in flatten(file_paths)
        ]

        await asyncio.gather(*tasks)

        workflow.logger.info("Uploaded pii to elasticsearch...")
