from contextlib import asynccontextmanager

from dishka.integrations.fastapi import FromDishka, inject, setup_dishka
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from di.container import container
from src.core.logger import logger
from src.modules.activities.presentation.routes.activity import activity_router
from src.modules.activities.presentation.routes.schedule import schedule_router
from src.modules.activity_records.presentation.routes import activity_record_router
from src.modules.users.presentation.routes import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started")
    yield
    logger.info("Application stopped")
    await container.close()


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(activity_router)
app.include_router(activity_record_router)
app.include_router(schedule_router)

setup_dishka(container=container, app=app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/health/db")
@inject
async def health_db(session: FromDishka[AsyncSession]) -> dict[str, int | None]:
    result = await session.execute(text("SELECT 1"))
    return {"db": result.scalar()}
