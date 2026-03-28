import argparse
import asyncio
import time

from app.config import config
from app.interactor.event.temporal.execute_workflows import execute_file_ingestion
from app.interactor.event.temporal.workflows import ProcessFileResult


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a Temporal workflow against an input file."
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="Path to the input file (default: ./data/input/wallets.jsonl)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size for processing (default: workflow default)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    input_file: str = args.input_file
    batch_size: int = args.batch_size or config.DEFAULT_INGESTION_BATCH_SIZE

    print("Submitting ingestion task...")
    print(f"  Input file  : {input_file}")
    print(f"  Batch size  : {batch_size}")

    start: float = time.time()

    kwargs = {"file_path": input_file, "batch_size": batch_size}

    result: ProcessFileResult = await execute_file_ingestion(**kwargs)

    elapsed: float = time.time() - start

    print(f"\n{'=' * 40}")
    print(f"  Chunks processed : {result.total_chunks}")
    print(f"  Total records    : {result.total_records:,}")
    print(f"  Valid            : {result.total_valid:,}")
    print(f"  Invalid          : {result.total_invalid:,}")
    print(f"  Wall clock time  : {elapsed:.2f}s")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    asyncio.run(main())
