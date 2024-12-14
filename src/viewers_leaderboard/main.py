from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.viewers_leaderboard.lifespan import app_lifespan
import src.viewers_leaderboard.webhook.routes as webhook_routes
import src.viewers_leaderboard.ranking.routes as ranking_routes

app = FastAPI(lifespan=app_lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok"}


app.include_router(webhook_routes.router)
app.include_router(ranking_routes.router)
