import asyncio
import statistics
import typing

import logging
import discord.ext.commands
import aoe4_discord
import aoe4_discord.models
import aoe4_discord.consts
import aoe4_discord.stats
import aoe4_discord.client

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
async def ls(ctx: discord.ext.commands.Context, profile: aoe4_discord.consts.Idiot) -> None:
    async with aoe4_discord.client.AOE4Client() as client:
        stats: dict[str, typing.Any] | None = await client.get_player_profile_and_stats(profile)

        if stats is None:
            await ctx.channel.send(f"Couldn't read stats for profile: {profile}")
            return

        total_ls = stats["modes"][aoe4_discord.consts.Elo.rm_solo]["losses_count"] + \
            stats["modes"][aoe4_discord.consts.Elo.rm_2v2]["losses_count"] + \
            stats["modes"][aoe4_discord.consts.Elo.rm_3v3]["losses_count"] + \
            stats["modes"][aoe4_discord.consts.Elo.rm_4v4]["losses_count"]

        await ctx.channel.send(f'Total {stats["name"]} Ls: {total_ls}')


@AOE4DiscordBot.command(name="apm", help="Retrieve APM for the last game played by hardcoded player IDs.")
async def apm(ctx: discord.ext.commands.Context, profile: aoe4_discord.consts.Idiot) -> None:

    async with aoe4_discord.client.AOE4Client() as client:
        last_games = await client.get_games(profile)

        game_apms = await asyncio.gather(*(client.get_game_apm(profile, game["game_id"]) for game in last_games))
        game_apms = [game_apm for game_apm in game_apms if game_apm]
        last_game_apm, other_apms = game_apms[0], game_apms[1:]

        average_apm = round(sum(other_apms) / len(other_apms))
        percent_change = aoe4_discord.stats.calculate_percentage_change(average_apm, last_game_apm)

        if percent_change > 0:
            result = "faster"
            emoji = "🔥"
        else:
            result = "slower"
            emoji = "🐢"

        if percent_change > 10:
            emoji = "🚀"

        if percent_change < -10:
            emoji = "🦥"

        percent_change = abs(percent_change)

        embed = discord.Embed(
            title=f"{profile.title()} Last APM: {round(percent_change)}% {result} than average {emoji}",
            description=f"Last Game APM: {last_game_apm}\n"
                        f"Average APM: {average_apm} over {len(other_apms)} games",
            color=discord.Color.blue()
        )
        await ctx.channel.send(embed=embed)


@AOE4DiscordBot.command(name="relics", help="Retrieve the last game with relic information.")
async def relics(ctx: discord.ext.commands.Context, profile: typing.Optional[aoe4_discord.consts.Idiot] = None) -> None:
    if not profile:
        profile = aoe4_discord.consts.Idiot.from_discord_username(ctx.author.name)

    async with aoe4_discord.client.AOE4Client() as client:
        last_game = await client.get_last_game(profile)

        if not last_game:
            await ctx.send("No last game found for the specified profile.")
            return

        game_summary = await client.get_game_summary(profile, last_game["game_id"])

    if not game_summary:
        await ctx.send("No game summary available yet. Be patient bitch")

    team: list[aoe4_discord.models.PlayerProfile] = [
        player
        for player in game_summary["players"]
        if player["profileId"] in [i.__getattribute__("profile_id") for i in aoe4_discord.consts.Idiot]
    ]

    best_kill_weighted_by_kd, bkwkd_player = 0, ""
    highest_avg_military, ham_player = 0, ""
    highest_avg_economy, hae_player = 0, ""

    for player in team:
        stats = player["_stats"]

        kills = stats["sqkill"]
        lost = stats["sqlost"]
        kd = kills / lost

        avg_military = statistics.mean(player["resources"]["military"])
        avg_economy = statistics.mean(player["resources"]["economy"])

        kills_weighted_by_kd = kills * kd

        if kills_weighted_by_kd > best_kill_weighted_by_kd:
            best_kill_weighted_by_kd, bkwkd_player = kills_weighted_by_kd, player["name"]

        if avg_military > highest_avg_military:
            highest_avg_military, ham_player = avg_military, player["name"]

        if avg_economy > highest_avg_economy:
            highest_avg_economy, hae_player = avg_economy, player["name"]

    embed = discord.Embed(title="Relic Awards for Last Game", color=discord.Color.blue())
    embed.add_field(name="Outcome", value=f"{team[0]["result"]}", inline=True)
    embed.add_field(name="End Reason", value=f"{game_summary["winReason"]}", inline=False)
    embed.add_field(name="Duration", value=f"{last_game['duration']} seconds", inline=False)
    embed.add_field(name="Map", value=last_game["map"], inline=False)
    embed.add_field(name="Game Mode", value=last_game["kind"], inline=False)

    relic_emote = AOE4DiscordBot.get_emoji(aoe4_discord.consts.RELIC_EMOJI_ID_IN_EGGS)
    embed.add_field(
        name="Best Kill Score",
        value=f"{relic_emote} {bkwkd_player} ({round(best_kill_weighted_by_kd)})",
        inline=False
    )
    embed.add_field(
        name="Best Military",
        value=f"{relic_emote} {ham_player} ({round(highest_avg_military)})",
        inline=False
    )
    embed.add_field(
        name="Best Economy",
        value=f"{relic_emote} {hae_player} ({round(highest_avg_economy)})",
        inline=False
    )

    await ctx.send(embed=embed)
