import typing

import logging
import discord.ext.commands
import aoe4_discord

from aoe4_discord.consts import Elo, Idiot

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
async def ls(ctx: discord.ext.commands.Context, profile: Idiot) -> None:
    async with aoe4_discord.AOE4Client() as client:
        stats: dict[str, typing.Any] | None = await client.get_player_profile_and_stats(profile)

        if stats is None:
            await ctx.channel.send(f"Couldn't read stats for profile: {profile}")
            return

        total_ls = stats["modes"][Elo.rm_solo]["losses_count"] + \
                   stats["modes"][Elo.rm_2v2]["losses_count"] + \
                   stats["modes"][Elo.rm_3v3]["losses_count"] + \
                   stats["modes"][Elo.rm_4v4]["losses_count"]

        await ctx.channel.send(f'Total {stats["name"]} Ls: {total_ls}')


@AOE4DiscordBot.command(name="lastapm", help="Retrieve APM for the last game played by hardcoded player IDs.")
async def lastapm(ctx: discord.ext.commands.Context, profile: Idiot) -> None:

    async with aoe4_discord.AOE4Client() as client:
        last_game_id = await client.get_last_game_id(profile)
        last_game_apm = await client.get_game_apm(profile, game_id=last_game_id)

        await ctx.channel.send(f"Last Game APM: {last_game_apm}")
