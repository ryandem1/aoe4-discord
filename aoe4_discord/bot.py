import typing

import discord
import logging
import discord.ext.commands
import aoe4_discord

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True

AOE4DiscordBot = discord.ext.commands.Bot(command_prefix="/", intents=intents)


@AOE4DiscordBot.event
async def on_ready() -> None:
    logger.info("Initialized bot")


@AOE4DiscordBot.command(name="ls", help="Retrieve player profile and stats by profile ID.")
async def ls(ctx: discord.ext.commands.Context, profile_id: int) -> None:
    async with aoe4_discord.AOE4Client() as client:
        stats: dict[str, typing.Any] | None = await client.get_player_profile_and_stats(profile_id)
        logger.info(stats)

        if stats is None:
            await ctx.channel.send(f"Couldn't read stats for profile: {profile_id}")
            return

        total_ls = stats["modes"][aoe4_discord.GameMode.rm_solo]["losses_count"] + \
            stats["modes"][aoe4_discord.GameMode.rm_2v2]["losses_count"] + \
            stats["modes"][aoe4_discord.GameMode.rm_3v3]["losses_count"] + \
            stats["modes"][aoe4_discord.GameMode.rm_4v4]["losses_count"]

        await ctx.channel.send(f'Total {stats["name"]} Ls: {total_ls}')
