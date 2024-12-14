from datetime import datetime
import pytest
from fastapi import HTTPException
from src.viewers_leaderboard.webhook.transport import (
    parse_active_stream_override_header,
)
from src.viewers_leaderboard.twitch.models import TwitchStream


def test_parse_active_stream_override_header_valid():
    now = datetime.now()
    active_stream_broadcaster_id_override = "12345"
    active_stream_started_at_override = str(now)

    result = parse_active_stream_override_header(
        active_stream_broadcaster_id_override=active_stream_broadcaster_id_override,
        active_stream_started_at_override=active_stream_started_at_override,
    )

    assert isinstance(result, TwitchStream)
    assert result.broadcaster_id == active_stream_broadcaster_id_override
    assert result.started_at == now


def test_parse_active_stream_override_header_invalid_json():
    active_stream_broadcaster_id_override = "12345"
    active_stream_started_at_override = "invalid-date"

    with pytest.raises(HTTPException) as exc_info:
        parse_active_stream_override_header(
            active_stream_broadcaster_id_override=active_stream_broadcaster_id_override,
            active_stream_started_at_override=active_stream_started_at_override,
        )

    assert exc_info.value.status_code == 400
    assert "Invalid active stream overrides" in exc_info.value.detail


def test_parse_active_stream_override_header_missing_header():
    result = parse_active_stream_override_header(
        active_stream_broadcaster_id_override=None,
        active_stream_started_at_override=None,
    )

    assert result is None
