import logging
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import FromDishka, inject, setup_dishka
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from entrypoints.container import create_container
from modules.activity.presentation.routes.activity import activity_router
from modules.activity.presentation.routes.activity_schedule import activity_schedule_router
from modules.activity_record.presentation.routes import activity_record_router
from modules.auth.presentation.exception_handlers import setup_auth_exception_handlers
from modules.auth.presentation.routes import auth_router
from modules.user.presentation.exception_handlers import setup_user_exception_handlers
from modules.user.presentation.routes import user_router
from shared.logger import setup_logging

setup_logging()
container = create_container()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started")
    yield
    logger.info("Application stopped")
    await container.close()


app = FastAPI(lifespan=lifespan)

setup_user_exception_handlers(app)
setup_auth_exception_handlers(app)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(activity_router)
app.include_router(activity_record_router)
app.include_router(activity_schedule_router)

setup_dishka(container=container, app=app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/health/db")
@inject
async def health_db(session: FromDishka[AsyncSession]) -> dict[str, int | None]:
    result = await session.execute(text("SELECT 1"))
    return {"db": result.scalar()}
