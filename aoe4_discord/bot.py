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
        stats = await client.get_player_profile_and_stats(profile_id)
        logger.info(stats)
        total_ls = stats["modes"]["rm_3v3_elo"]["losses_count"] + \
                   stats["modes"]["rm_2v2_elo"]["losses_count"] + \
                   stats["modes"]["rm_solo"]["losses_count"] + \
                   stats["modes"]["rm_4v4_elo"]["losses_count"]

        await ctx.channel.send(f'Total {stats["name"]} Ls: {total_ls}')
