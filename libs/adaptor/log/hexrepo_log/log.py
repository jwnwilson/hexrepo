import json
import logging
import os
import sys
import traceback
import uuid
from contextlib import contextmanager
from types import TracebackType
from typing import Optional

from loguru import logger

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
LOG_JSON = True if os.environ.get("LOG_JSON") else False
LOG_MULTIPROCESS = True if os.environ.get("LOG_MULTIPROCESS") else False


def serialize(record) -> str:
    exception = record.get("exception")
    trace = None
    if exception:
        trace = "".join(traceback.format_exception(*exception))
    subset = dict(
        severity=record["level"].name,
        message=record["message"],
        elapsed=record["elapsed"],
        exception=trace,
        file=dict(name=record["file"].name, path=record["file"].path),
        function=record["function"],
        line=record["line"],
        module=record["module"],
        name=record["name"],
        process=dict(id=record["process"].id, name=record["process"].name),
        thread=dict(id=record["thread"].id, name=record["thread"].name),
        time=record["time"],
        labels=record["extra"],
    )
    return json.dumps(subset)


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def trim_exception(exc: Exception):
    """trim system packages from the exception printout"""
    from distutils.sysconfig import get_python_lib

    value: Exception = exc
    tb: TracebackType = exc.__traceback__

    lib_dir: str = get_python_lib(True, False).lower()
    current_tb: TracebackType = tb
    prev_node = None

    while current_tb:
        fn = current_tb.tb_frame.f_code.co_filename
        if fn.lower().startswith(lib_dir):
            if prev_node:
                prev_node.tb_next = current_tb.tb_next
            else:
                tb = current_tb.tb_next
        else:
            prev_node = current_tb
        current_tb = current_tb.tb_next

    logger.exception(value.with_traceback(tb))


def setup_logger():
    level: str = LOG_LEVEL

    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    if LOG_JSON:
        logger.configure(
            handlers=[
                {
                    "sink": serialize,
                    "serialize": json,
                    "diagnose": True,
                    "backtrace": True,
                    "catch": True,
                    "enqueue": LOG_MULTIPROCESS,
                }
            ]
        )
    else:
        format: str = "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</g> | <level>{level}</level> | <c>{name}</c>:<c>{function}</c>:<c>{line}</c> - <level>{message}</level> | <y>{extra}</y>"  # noqa: E501
        logger.configure(
            handlers=[
                dict(
                    sink=sys.stdout,
                    level=level,
                    backtrace=False,
                    diagnose=True,
                    colorize=True,
                    format=format,
                    enqueue=LOG_MULTIPROCESS,
                )
            ]
        )
    return logger


@contextmanager
def log_manager(correlation_id: Optional[str] = None):
    correlation_id: str = correlation_id or str(uuid.uuid4())
    with logger.contextualize(correlation_id=correlation_id):
        try:
            yield logger
        except Exception as exc:
            trim_exception(exc)
