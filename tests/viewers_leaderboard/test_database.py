from unittest.mock import MagicMock, AsyncMock, patch, ANY
from beanie import Document
from beanie.odm.documents import DocumentWithSoftDelete
from polyfactory.pytest_plugin import register_fixture
from polyfactory.factories.pydantic_factory import ModelFactory
from src.viewers_leaderboard.settings import Settings
from src.viewers_leaderboard.database import (
    setup_database_connection,
    shutdown_database_connection,
)


@register_fixture
class SettingsMock(ModelFactory[Settings]): ...


@patch("src.viewers_leaderboard.database.AsyncIOMotorClient", new_callable=MagicMock)
@patch("src.viewers_leaderboard.database.init_beanie", new_callable=AsyncMock)
async def test_setup_database_connection_should_create_client_and_init_beanie(
    init_beanie_mock: AsyncMock,
    motor_client_mock: MagicMock,
    settings_mock: SettingsMock,
):
    settings: Settings = settings_mock.build()
    app = MagicMock()
    db_mock = MagicMock()

    motor_client_mock.return_value = {
        f"{settings.mongo_db_name}": db_mock,
    }

    with patch("src.viewers_leaderboard.database.get_settings", return_value=settings):
        await setup_database_connection(app)

    motor_client_mock.assert_called_once_with(settings.mongo_conn_str)

    init_beanie_mock.assert_awaited_once_with(
        database=db_mock,
        document_models=ANY,
    )

    assert app.db_client == motor_client_mock()


@patch("src.viewers_leaderboard.database.AsyncIOMotorClient", new_callable=MagicMock)
@patch("src.viewers_leaderboard.database.init_beanie", new_callable=AsyncMock)
async def test_setup_database_connection_should_init_all_document_models(
    init_beanie_mock: AsyncMock,
    motor_client_mock: MagicMock,
):
    app = MagicMock()

    await setup_database_connection(app)

    motor_client_mock.assert_called_once()

    user_defined_document_models = set(Document.__subclasses__())
    user_defined_document_models.remove(DocumentWithSoftDelete)

    init_beanie_mock.assert_awaited_once()
    (_, init_beanie_await_args) = init_beanie_mock.await_args
    call_arg_document_models = init_beanie_await_args["document_models"]

    assert set(call_arg_document_models) == user_defined_document_models


async def test_shutdown_database_connection_closes_db_connection():
    app = MagicMock()

    await shutdown_database_connection(app)

    app.db_client.close.assert_called_once()
