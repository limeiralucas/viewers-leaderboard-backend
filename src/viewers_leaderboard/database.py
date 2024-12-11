from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.viewers_leaderboard.log import logger
from src.viewers_leaderboard.config import get_settings

from src.viewers_leaderboard.ranking.models import Score


async def setup_database_connection(app: FastAPI):
    settings = get_settings()

    logger.info("Setting up database connection...")
    app.db_client = AsyncIOMotorClient(settings.mongo_conn_str)

    logger.info("Initializing ODM...")
    await init_beanie(
        database=app.db_client[settings.mongo_db_name], document_models=[Score]
    )

    logger.info("Database connected.")


async def shutdown_database_connection(app: FastAPI):
    logger.info("Shutting down database connection...")
    app.db_client.close()

    logger.info("Database disconnected.")
