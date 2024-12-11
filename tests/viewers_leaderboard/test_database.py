from unittest.mock import MagicMock, AsyncMock, patch, ANY
from beanie import Document
from beanie.odm.documents import DocumentWithSoftDelete
from polyfactory.pytest_plugin import register_fixture
from polyfactory.factories.pydantic_factory import ModelFactory
from src.viewers_leaderboard.config import Config
from src.viewers_leaderboard.database import setup_database_connection

@register_fixture
class SettingsMock(ModelFactory[Config]): ...

@patch("src.viewers_leaderboard.database.AsyncIOMotorClient", new_callable=MagicMock)
@patch("src.viewers_leaderboard.database.init_beanie", new_callable=AsyncMock)
async def test_setup_database_connection_should_create_client_and_init_beanie(
    init_beanie_mock: AsyncMock,
    motor_client_mock: MagicMock,
    settings_mock: SettingsMock
):
    settings: Config = settings_mock.build()
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

@patch("src.viewers_leaderboard.database.AsyncIOMotorClient", new_callable=MagicMock)
@patch("src.viewers_leaderboard.database.init_beanie", new_callable=AsyncMock)
async def test_setup_database_connection_should_init_all_document_models(
    init_beanie_mock: AsyncMock,
    motor_client_mock: MagicMock,
):
    app = MagicMock()

    await setup_database_connection(app)

    motor_client_mock.assert_called_once()

    user_defined_document_models = Document.__subclasses__()
    user_defined_document_models.remove(DocumentWithSoftDelete)

    init_beanie_mock.assert_awaited_once_with(
        database=ANY,
        document_models=user_defined_document_models,
    )
    