import os
from typing import Optional

import orjson
from pydantic import BaseModel


# This should use a storage adaptor
def write_records(
    record_list: list[BaseModel],
    filepath: str,
    record_fields: Optional[list[str]] = None,
) -> str:
    if not record_list:
        return
    fields: list[str] = record_fields or list(record_list[0].__class__.model_fields)
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(filepath, "w") as f:
        for record in record_list:
            row = {field: getattr(record, field) for field in fields}
            f.write(orjson.dumps(row).decode("utf-8") + "\n")

    return filepath
