from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.viewers_leaderboard.database import (
    setup_database_connection,
    shutdown_database_connection,
)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await setup_database_connection(app)
    yield
    await shutdown_database_connection(app)
