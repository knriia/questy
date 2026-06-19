from fastapi import FastAPI
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka, FromDishka, inject
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.container import container
from src.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started")
    yield
    logger.info("Application stopped")
    await container.close()


app = FastAPI(lifespan=lifespan)
setup_dishka(container=container, app=app)


@app.get("/health")
async def health():
    return {"message": "Hello World"}


@app.get("/health/db")
@inject
async def health_db(session: FromDishka[AsyncSession]):
    result = await session.execute(text("SELECT 1"))
    return {"db": result.scalar()}

