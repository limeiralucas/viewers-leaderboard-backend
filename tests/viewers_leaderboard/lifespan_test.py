from unittest.mock import MagicMock, patch
import pytest
from src.viewers_leaderboard.chat import bot
from src.viewers_leaderboard.lifespan import app_lifespan

@pytest.mark.asyncio
async def test_app_lifespan_start_bot_task_and_cancels_on_teardown():
    app_mock = MagicMock()

    with patch("asyncio.get_event_loop") as mock_get_event_loop:
        mock_loop = MagicMock()
        mock_get_event_loop.return_value = mock_loop

        with patch.object(bot, "start", MagicMock()) as bot_start_mock:
            async with app_lifespan(app_mock):
                bot_start_mock.assert_called_once()

                mock_loop.create_task.assert_called_once_with(bot_start_mock())

        task = mock_loop.create_task.return_value
        task.cancel.assert_called_once()
