from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router_v1 = APIRouter()


@router_v1.post("/", include_in_schema=True)
def signup() -> JSONResponse:
    
    return JSONResponse(
        content={"status_message": "OK"},
        status_code=status.HTTP_200_OK,
    )
