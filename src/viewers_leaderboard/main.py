from fastapi import FastAPI
import src.viewers_leaderboard.webhook.routes as webhook_routes

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}


app.include_router(webhook_routes.router)
