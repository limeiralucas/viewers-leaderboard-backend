from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.viewers_leaderboard.database import (
    setup_database_connection,
    shutdown_database_connection,
)
import src.viewers_leaderboard.webhook.routes as webhook_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_database_connection(app)
    yield
    await shutdown_database_connection(app)


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "ok"}


app.include_router(webhook_routes.router)
