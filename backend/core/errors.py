import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from backend.schemas.common import ErrorDetail, ErrorResponse, ErrorSchema

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.error = ErrorSchema(code=code, message=message)


def error_response(status_code: int, error: ErrorSchema) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=error).model_dump(mode="json"),
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_error(request: Request, exc: AppException) -> JSONResponse:
        return error_response(exc.status_code, exc.error)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Do not echo image bytes or user input into errors.
        details = [ErrorDetail(field=".".join(map(str, item["loc"])), message=item["msg"])
                   for item in exc.errors()]
        return error_response(422, ErrorSchema(
            code="VALIDATION_ERROR", message="Request validation failed", details=details,
        ))

    @app.exception_handler(HTTPException)
    async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return error_response(exc.status_code, ErrorSchema(
            code="NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR",
            message=str(exc.detail),
        ))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled API error", exc_info=exc)
        return error_response(500, ErrorSchema(
            code="INTERNAL_ERROR", message="An internal error occurred",
        ))
