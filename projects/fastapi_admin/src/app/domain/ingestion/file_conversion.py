import csv

import orjson


def csv_to_jsonl(input_file: str, output_file: str, chunk_size: int = 10_000) -> None:
    with (
        open(input_file, "r", encoding="utf-8") as csv_file,
        open(output_file, "wb") as jsonl_file,
    ):  # binary mode for orjson
        reader = csv.DictReader(csv_file)
        buffer = []

        for row in reader:
            buffer.append(orjson.dumps(dict(row)))
            if len(buffer) >= chunk_size:
                jsonl_file.write(b"\n".join(buffer) + b"\n")
                buffer.clear()

        if buffer:
            jsonl_file.write(b"\n".join(buffer) + b"\n")


def json_to_jsonl(input_file: str, output_file: str, chunk_size: int = 10_000) -> None:
    with open(input_file, "rb") as json_file:  # binary mode for orjson
        data = orjson.loads(json_file.read())

    with open(output_file, "wb") as jsonl_file:
        items = data if isinstance(data, list) else [data]
        buffer = []

        for item in items:
            buffer.append(orjson.dumps(item))
            if len(buffer) >= chunk_size:
                jsonl_file.write(b"\n".join(buffer) + b"\n")
                buffer.clear()

        if buffer:
            jsonl_file.write(b"\n".join(buffer) + b"\n")


def convert_to_jsonl(
    input_file: str, output_file: str = None, chunk_size: int = 10_000
) -> None:
    if output_file is None:
        output_file = input_file.rsplit(".", 1)[0] + ".jsonl"

    ext = input_file.rsplit(".", 1)[-1].lower()

    if ext == "csv":
        csv_to_jsonl(input_file, output_file, chunk_size)
    elif ext == "json":
        json_to_jsonl(input_file, output_file, chunk_size)
    else:
        raise ValueError(f"Unsupported file type: .{ext} (expected .csv or .json)")
