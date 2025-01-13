from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from loguru import logger

router_v1 = APIRouter()


@router_v1.get("/", include_in_schema=True)
def healthcheck() -> JSONResponse:
    logger.info("test log")
    return JSONResponse(
        content={"status_message": "OK"},
        status_code=status.HTTP_200_OK,
    )
