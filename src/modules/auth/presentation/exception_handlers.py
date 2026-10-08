import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from modules.auth.domain.exceptions import CredentialsValidationError, InvalidPasswordError

logger = logging.getLogger(__name__)


async def handle_invalid_credentials_error(
    request: Request,
    error: CredentialsValidationError,
) -> JSONResponse:
    logger.warning(
        "Invalid credentials: reason=%s path=%s",
        error.code,
        request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": {
                "code": error.code,
                "message": str(error),
            }
        },
    )


async def handle_invalid_password_error(
    request: Request,
    error: InvalidPasswordError,
) -> JSONResponse:
    logger.warning(
        "Invalid password: reason=%s path=%s",
        error.code,
        request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": {
                "code": error.code,
                "message": str(error),
            }
        },
    )


def setup_auth_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        CredentialsValidationError,
        handle_invalid_credentials_error,
    )

    app.add_exception_handler(
        InvalidPasswordError,
        handle_invalid_password_error,
    )
