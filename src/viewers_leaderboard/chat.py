from twitchio import Channel
from twitchio.ext import commands
from src.viewers_leaderboard.config import get_settings
from src.viewers_leaderboard.log import logger


class TwitchBot(commands.Bot):
    def __init__(self, token: str, initial_channels: list[str] | None = None):
        logger.info("Initializing bot...")
        if initial_channels is None:
            initial_channels = []

        super().__init__(token=token, prefix="!", initial_channels=initial_channels)

    async def event_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.nick}")

    async def event_channel_joined(self, channel: Channel):
        logger.info(f"Logged to {channel.name}")

    async def event_message(self, message):
        logger.info(
            f"<{message.channel.name}> {message.author.name}: {message.content}"
        )


bot = TwitchBot(get_settings().twitch_oauth_token)
