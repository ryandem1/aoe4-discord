import discord
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


class AOE4DiscordBot(discord.Client):
    name = "aoe4"
    intents = discord.Intents.default()

    def __init__(self, *, intents: discord.Intents | None = None, **kwargs):
        intents = intents or discord.Intents.default()
        super().__init__(intents=intents, **kwargs)

    async def on_ready(self) -> None:
        logger.info(f"Initialized bot: {self.name}")
