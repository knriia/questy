import logging
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import FromDishka, inject, setup_dishka
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from entrypoints.container import create_container
from modules.activities.presentation.routes.activity import activity_router
from modules.activities.presentation.routes.activity_schedule import activity_schedule_router
from modules.activity_records.presentation.routes import activity_record_router
from modules.users.presentation.exception_handlers import setup_user_exception_handlers
from modules.users.presentation.routes import user_router
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
