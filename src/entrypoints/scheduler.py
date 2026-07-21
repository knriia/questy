import asyncio
import logging
from datetime import UTC, datetime

from entrypoints.container import create_container
from modules.activities.application.services.activity_schedule_dispatcher import ActivityScheduleDispatcher
from shared.logger import setup_logging

setup_logging()

logger = logging.getLogger(__name__)


async def run_scheduler():
    container = create_container()
    logger.info("Scheduler started")
    try:
        while True:
            now = datetime.now(UTC)
            async with container() as request_container:
                dispatcher = await request_container.get(ActivityScheduleDispatcher)
                await dispatcher.dispatch_due(now)

            await asyncio.sleep(60)

    finally:
        logger.info("Scheduler stopped")
        await container.close()


if __name__ == "__main__":
    asyncio.run(run_scheduler())
