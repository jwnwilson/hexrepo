import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
import orjson
import tqdm
from loguru import logger
from pydantic import ValidationError
from temporalio import activity
from tqdm.asyncio import tqdm as atqdm
from hexrepo_cache.redis import CacheInterface, RedisCache
from hexrepo_search.elastisearch import ElasticsearchClient
from hexrepo_db.sql.uow import BaseSqlUOW

from app.config import config
from app.domain.ingestion.activity_logic import write_records
from app.domain.ingestion.file_conversion import convert_to_jsonl as convert_to_jsonl_fn
from app.domain.ingestion.input_data import InputData

OUPUT_DATA_PATH = "./data/output"


@dataclass
class ChunkResult[BaseModel]:
    chunk_id: int
    total: int
    valid: int
    invalid: int
    validated_filename: str
    results: list[BaseModel]


@activity.defn
async def convert_to_jsonl(input_file: str, output_file: str) -> str:
    """
    Convert files to json
    """
    return convert_to_jsonl_fn(input_file, output_file)


@activity.defn
async def get_chunk_offsets(file_path: str, chunk_size: int) -> list[list[int]]:
    """
    Scan the file once and return a list of [byte_start, byte_end] pairs,
    one per chunk. This is so we can use seek() for vroom vroom!
    """
    activity.logger.info(f"Scanning {file_path} with chunk_size={chunk_size}")

    offsets = []
    chunk_start = 0
    count = 0

    with open(file_path, "rb") as f:
        while True:
            line = f.readline()
            if not line:
                # End of file — flush any remaining lines as the last chunk
                if count > 0:
                    offsets.append([chunk_start, f.tell()])
                break

            count += 1

            if count == chunk_size:
                offsets.append([chunk_start, f.tell()])
                chunk_start = f.tell()
                count = 0

    activity.logger.info(
        f"Found {sum(1 for _ in open(file_path))} total lines, split into {len(offsets)} chunks"
    )
    return offsets


@activity.defn
async def validate_wallets(
    file_path: str,
    chunk_id: int,
    byte_start: int,
    byte_end: int,
) -> ChunkResult:
    """
    Read a byte range from the file, validate each record,
    and write valid/invalid records to separate output files.
    Think of this as pushing to DB, sorta

    ## Demo note: This would be better as a different activity in case it fails. ##
    """
    activity.logger.info(
        f"Processing chunk {chunk_id:04d} (bytes {byte_start}-{byte_end})"
    )
    # parser = InputDataParser()
    raise NotImplementedError
    # return parser.parse_input_data(file_path, chunk_id, byte_start, byte_end, CreateAddressDTO, lambda x: CreateAddressDTO(**x))


@activity.defn
async def load_wallet_data(
    file_path: str,
) -> ChunkResult:
    if not file_path.endswith(".csv"):
        raise NotImplementedError("Bulk data loading only supports .csv files")

    activity.logger.info(f"Loading file {file_path} into db)")

    # Create db session and transaction
    uow = BaseSqlUOW(db_url=config.DB_PG_URL, required_filters=None)
    async with uow.transaction():
        # This needs to be moved to db adaptor
        connection = await uow.session.connection()
        raw_connection = await connection.get_raw_connection()
        psy_conn = raw_connection.driver_connection

        async with psy_conn.cursor().copy(
            "COPY wallet_address (address, chain) FROM STDIN WITH CSV HEADER"
        ) as copy:
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):  # 64KB chunks
                    await copy.write(chunk)

    activity.logger.info(f"Loaded file {file_path} into db)")


class InputDataParser:
    def __init__(self):
        os.makedirs(f"{OUPUT_DATA_PATH}/valid", exist_ok=True)
        os.makedirs(f"{OUPUT_DATA_PATH}/invalid", exist_ok=True)

    def extract_list(self, field) -> list[str]:
        if not field or field == "null":
            return []
        try:
            field = orjson.loads(field)
        except orjson.JSONEncodeError:
            pass
        if isinstance(field, list):
            result = []
            for item in field:
                if isinstance(item, dict):
                    val = item.get("value")
                else:
                    val = item
                if val and val != "null":
                    result.append(str(val))
            return result
        if isinstance(field, str) and field != "null":
            return [field]
        return []

    def extract_str(self, field) -> str:
        if not field or field == "null":
            return ""
        if isinstance(field, list) and field:
            item = field[0]
            return str(item.get("value", "") if isinstance(item, dict) else item)
        return str(field)

    def parse_logic(self, json_data: dict):
        return InputData(
            row_id=self.extract_str(json_data.get("row_id")),
            source=self.extract_str(json_data.get("source")),
            scraper_name=self.extract_str(json_data.get("scraper_name")),
            wallets=self.extract_list(json_data.get("wallets")),
            emails=self.extract_list(json_data.get("emails")),
            phones=self.extract_list(json_data.get("phones")),
            ibans=self.extract_list(json_data.get("ibans")),
            platforms=self.extract_list(json_data.get("platforms")),
            credit_cards=self.extract_list(json_data.get("credit_cards")),
            names=self.extract_list(json_data.get("names")),
            ip_addresses=self.extract_list(json_data.get("ip_addresses")),
            countries=self.extract_list(json_data.get("countries")),
            currencies=self.extract_list(json_data.get("currencies")),
            usernames=self.extract_list(json_data.get("usernames")),
            profile_links=self.extract_list(json_data.get("profile_links")),
        )

    def parse_input_data(
        self,
        file_path: str,
        byte_start: int,
        byte_end: int,
    ) -> dict[str, InputData]:
        row_data: dict[str, InputData] = {}

        # Seek into the file
        with open(file_path, "rb") as f:
            f.seek(byte_start)
            raw = f.read(byte_end - byte_start)

        lines = raw.decode("utf-8").strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                record = orjson.loads(line)
                input_data: InputData = self.parse_logic(record)
                # Group and combine input data by row id
                if input_data.row_id not in row_data:
                    row_data[input_data.row_id] = input_data
                else:
                    row_data[input_data.row_id] = (
                        input_data + row_data[input_data.row_id]
                    )
            except ValidationError as e:
                logger.error(f"Error parsing wallet: {e}")

        return row_data


@activity.defn
async def map_pii_to_node_ids(
    file_path: str,
    chunk_id: int,
    byte_start: int,
    byte_end: int,
) -> list[str]:
    existing_data_filename: str = f"existing_pii_node_{chunk_id}.jsonl"
    new_data_filename: str = f"new_pii_nodes_{chunk_id}.jsonl"
    existing_data_filepath: str = (
        f"{config.OUPUT_DATA_PATH}/valid/{existing_data_filename}"
    )
    new_data_filepath: str = f"{config.OUPUT_DATA_PATH}/valid/{new_data_filename}"

    if os.path.isfile(existing_data_filepath) and os.path.isfile(new_data_filepath):
        return [existing_data_filepath, new_data_filepath]

    # pii -> node_ids
    new_pii_nodes: list[InputData] = []
    existing_pii_nodes: list[InputData] = []
    # Get redis connection
    cache: CacheInterface = RedisCache()

    # Parse the input data
    activity.logger.info(
        f"Processing chunk {chunk_id:04d} (bytes {byte_start}-{byte_end})"
    )
    parser: InputDataParser = InputDataParser()
    # Group the data by row_id
    results: dict[str, InputData] = parser.parse_input_data(
        file_path,
        byte_start,
        byte_end,
    )
    # for each row_id search redis for pii
    for row_id in tqdm.tqdm(results):
        input_data: InputData = results[row_id]
        piis: list[str] = input_data.pii
        found_node_ids: list[str | None] = await cache.get_multi(piis)
        found_node_ids = [x for x in found_node_ids if x]
        # if found add to existing_nodes else create new node
        if found_node_ids:
            input_data.entity_id = found_node_ids[0]
            existing_pii_nodes.append(input_data)
        else:
            input_data.entity_id = str(uuid.uuid4())
            new_pii_nodes.append(input_data)
        await cache.set_mulit({pii: input_data.entity_id for pii in piis})

    logger.info(
        f"Found: {len(new_pii_nodes)} new nodes and {len(existing_pii_nodes)} existing nodes"
    )

    write_records(existing_pii_nodes, existing_data_filepath)
    write_records(new_pii_nodes, new_data_filepath)

    return [existing_data_filepath, new_data_filepath]


async def bulk_index_in_batches(
    client: ElasticsearchClient, documents: list[dict], batch_size: int = 5000
) -> None:
    total = len(documents)
    errors = []

    for start in range(0, total, batch_size):
        batch = documents[start : start + batch_size]
        result = await client.bulk_index(batch)
        errors.extend(result["errors"])
        print(f"Indexed {min(start + batch_size, total)}/{total} ...")

    print(f"\nDone. Total errors: {len(errors)}")
    if errors:
        print("First error:", errors[0])


async def iter_jsonl(
    path: str | Path, batch_size: int = 5000
) -> AsyncGenerator[list[dict], None]:
    """Async generator that yields batches of dicts from a JSONL file."""
    batch: list[dict] = []
    async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
        async for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            batch.append(orjson.loads(line))
            if len(batch) >= batch_size:
                yield batch
                batch = []
    if batch:
        yield batch


@activity.defn
async def index_records(pii_node_data_filepath: str):
    async with ElasticsearchClient("nodes") as es:
        if not await es.index_exists():
            logger.info("Createing ES index: nodes")
            await es.create_index()

        logger.info("Indexing documents in elasticsearch")

        async for batch in atqdm(iter_jsonl(pii_node_data_filepath)):
            await bulk_index_in_batches(es, batch)

        logger.info("Indexing documents complete")
