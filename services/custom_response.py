"""Create a custom response for change response status when it is validation error"""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = jsonable_encoder({"detail": exc.errors()})
    print(error)
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST, content={"message": "Validation Error", "error": error}
    )