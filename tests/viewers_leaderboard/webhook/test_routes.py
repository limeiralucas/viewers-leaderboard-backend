from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from src.viewers_leaderboard.main import app
from src.viewers_leaderboard.webhook.transport import ChallengePayload

client = TestClient(app)


@register_fixture
class ChallengePayloadFactory(ModelFactory[ChallengePayload]): ...


def test_webhook_endpoint_should_answer_challenge(
    challenge_payload_factory: ChallengePayloadFactory,
):
    payload: ChallengePayload = challenge_payload_factory.build()

    response = client.post(
        "/webhook",
        json=payload.model_dump(),
        headers={"twitch-eventsub-message-type": "webhook_callback_verification"},
    )

    assert response.status_code == 200
    assert response.headers.get("content-type") == "text/plain; charset=utf-8"
    assert response.text == payload.challenge
