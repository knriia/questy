import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from modules.users.domain.exceptions import UserConflictError, UserValidationError

logger = logging.getLogger(__name__)


async def handle_user_validation_error(
    request: Request,
    error: UserValidationError,
) -> JSONResponse:
    logger.info(
        "User input rejected: reason=%s path=%s",
        error.code,
        request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": {
                "code": error.code,
                "message": str(error),
            },
        },
    )


async def handle_user_conflict_error(
    request: Request,
    error: UserConflictError,
) -> JSONResponse:
    logger.warning(
        "User registration conflict: reason=%s path=%s",
        error.code,
        request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": {
                "code": error.code,
                "message": str(error),
            }
        },
    )


def setup_user_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        UserValidationError,
        handle_user_validation_error,
    )

    app.add_exception_handler(
        UserConflictError,
        handle_user_conflict_error,
    )
