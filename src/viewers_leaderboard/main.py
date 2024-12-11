from fastapi import FastAPI
from src.viewers_leaderboard.lifespan import app_lifespan
import src.viewers_leaderboard.webhook.routes as webhook_routes

app = FastAPI(lifespan=app_lifespan)


@app.get("/")
async def root():
    return {"status": "ok"}


app.include_router(webhook_routes.router)
