import asyncio
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

AOE4DiscordBot = discord.ext.commands.Bot(command_prefix="!", intents=intents)


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


@AOE4DiscordBot.command(name="apm", help="Retrieve APM for the last game played by hardcoded player IDs.")
async def apm(ctx: discord.ext.commands.Context, profile: Idiot) -> None:

    async with aoe4_discord.AOE4Client() as client:
        last_games = await client.get_games(profile)

        game_apms = await asyncio.gather(*(client.get_game_apm(profile, game["game_id"]) for game in last_games))
        last_game_apm, other_apms = game_apms[0], game_apms[1:36]

        average_apm = round(sum(other_apms) / len(other_apms))
        embed = discord.Embed(
            title="APM Statistics",
            description=f"Last Game APM: {last_game_apm}\n"
                        f"Average APM: {average_apm} over {len(other_apms)} games",
            color=discord.Color.blue()
        )
        await ctx.channel.send(embed=embed)

@AOE4DiscordBot.command(name="trophy", help="Retrieve the last game with trophy information for a specific profile.")
async def trophy(ctx: discord.ext.commands.Context, name: str) -> None:
    try:
        idiot = Idiot(name.lower())
        profile_id = idiot.profile_id
    except ValueError:
        await ctx.send(f"Invalid name: {name}. Please provide a valid name (jordaniel, ryan, or jared).")
        return

    async with aoe4_discord.AOE4Client() as client:
        last_game = await client.get_last_game_with_trophies(Idiot(idiot))

        if not last_game:
            await ctx.send("No last game found for the specified profile.")
            return

        embed = discord.Embed(title="Last Game", color=discord.Color.blue())
        embed.add_field(name="Game ID", value=last_game["game_id"], inline=False)
        embed.add_field(name="Started At", value=last_game["started_at"], inline=False)
        embed.add_field(name="Duration", value=f"{last_game['duration']} seconds", inline=False)
        embed.add_field(name="Map", value=last_game["map"], inline=False)
        embed.add_field(name="Game Mode", value=last_game["kind"], inline=False)

        if "trophies" in last_game:
            trophies = last_game["trophies"]
            embed.add_field(name="Most Kills", value=trophies["most_kills"], inline=False)
            embed.add_field(name="Most Units", value=trophies["largest_army"], inline=False)
            embed.add_field(name="Most Razed", value=trophies["most_razed"], inline=False)
            embed.add_field(name="Most Economic", value=trophies["most_economic"], inline=False)
        else:
            embed.add_field(name="Trophies", value="No trophy information available.", inline=False)

        for team in last_game["teams"]:
            for player in team:
                if player["profile_id"] == profile_id:
                    embed.add_field(name="Player", value=player["name"], inline=True)
                    embed.add_field(name="Civilization", value=player["civilization"], inline=True)
                    embed.add_field(name="Outcome", value=player["result"], inline=True)
                    break

        await ctx.send(embed=embed)