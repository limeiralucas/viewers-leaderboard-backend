from fastapi import FastAPI
from src.viewers_leaderboard.lifespan import app_lifespan

app = FastAPI(lifespan=app_lifespan)


@app.get("/")
async def root():
    return {"status": "ok"}
