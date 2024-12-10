from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from src.viewers_leaderboard.log import logger
from src.viewers_leaderboard.models import WebhookPayload

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(payload: WebhookPayload, request: Request):
    message_type = request.headers.get('twitch-eventsub-message-type')

    if message_type == "webhook_callback_verification":
        return PlainTextResponse(content=payload.subscription.challenge)

    logger.info(payload.model_dump_json())

    return {"status": "ok"}
