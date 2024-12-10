from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from src.viewers_leaderboard.main import app
from src.viewers_leaderboard.models import WebhookPayload

client = TestClient(app)

@register_fixture
class WebhookPayloadFactory(ModelFactory[WebhookPayload]): ...

def test_webhook_endpoint_should_answer_challenge(webhook_payload_factory: WebhookPayloadFactory):
    payload: WebhookPayload = webhook_payload_factory.build(subscription = {"challenge": "test-challenge"})

    response = client.post(
        "/webhook",
        json=payload.model_dump(),
        headers={"twitch-eventsub-message-type": "webhook_callback_verification"}
    )

    assert response.status_code == 200
    assert response.headers.get("content-type") == "text/plain; charset=utf-8"
    assert response.text == payload.subscription.challenge

def test_webhook_endpoint_returns_200(webhook_payload_factory: WebhookPayloadFactory):
    payload: WebhookPayload = webhook_payload_factory.build()

    response = client.post("/webhook", json=payload.model_dump())

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
