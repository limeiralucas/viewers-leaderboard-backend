from unittest.mock import MagicMock, AsyncMock, patch
from src.viewers_leaderboard.lifespan import app_lifespan


@patch(
    "src.viewers_leaderboard.lifespan.shutdown_database_connection",
    new_callable=AsyncMock,
)
@patch(
    "src.viewers_leaderboard.lifespan.setup_database_connection", new_callable=AsyncMock
)
async def test_app_lifespan_should_setup_and_shutdown_db_connection(
    setup_db_mock: AsyncMock, shutdown_db_mock: AsyncMock
):
    app = MagicMock()

    async with app_lifespan(app):
        setup_db_mock.assert_awaited_once_with(app)

    shutdown_db_mock.assert_awaited_once_with(app)
