from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from src.viewers_leaderboard.log import logger
from src.viewers_leaderboard.config import get_settings


async def setup_database_connection(app: FastAPI):
    settings = get_settings()

    logger.info("Setting up database connection...")
    app.db_client = AsyncIOMotorClient(settings.mongo_conn_str)
    app.db = app.db_client.get_database(settings.mongo_db_name)

    logger.info("Database connected.")


async def shutdown_database_connection(app: FastAPI):
    logger.info("Shutting down database connection...")
    app.db_client.close()

    logger.info("Database disconnected.")
