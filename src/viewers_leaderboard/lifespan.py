import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.viewers_leaderboard.chat import bot


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    loop = asyncio.get_event_loop()
    task = loop.create_task(bot.start())
    yield
    task.cancel()
