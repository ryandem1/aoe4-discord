import asyncio
import collections
import logging
import statistics
import typing

import discord.ext.commands

import aoe4_discord
import aoe4_discord.client
import aoe4_discord.consts
import aoe4_discord.models
import aoe4_discord.stats
import aoe4_discord.db

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
            await ctx.send("...")
            return

        game_summary = await client.get_game_summary(profile, last_game["game_id"])

    game_id = last_game["game_id"]

    if not game_summary:
        await ctx.send("praying. be patient bitch")

    team: list[aoe4_discord.models.PlayerProfile] = [
        player
        for player in game_summary["players"]
        if player["profileId"] in [i.__getattribute__("profile_id") for i in aoe4_discord.consts.Idiot]
    ]

    player_names = ", ".join(
        player["name"]
        for player in game_summary["players"]
    )

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

    result = team[0]["result"]
    end_reason = game_summary["winReason"]
    duration = last_game["duration"]
    map_ = last_game["map"]
    mode = last_game["kind"]

    game = aoe4_discord.models.GameRow(
        id=game_id,
        outcome=result,
        end_reason=end_reason,
        duration=duration,
        map=map_,
        game_mode=mode,
        players=player_names,
        created_at=None  # don't need it for writing
    )

    embed = discord.Embed(title="Relic Awards for Last Game", color=discord.Color.blue())
    embed.add_field(name="Outcome", value=f"{result}", inline=True)
    embed.add_field(name="End Reason", value=f"{end_reason}", inline=False)
    embed.add_field(name="Duration", value=f"{duration} seconds", inline=False)
    embed.add_field(name="Map", value=map_, inline=False)
    embed.add_field(name="Game Mode", value=mode, inline=False)

    relic_emote = AOE4DiscordBot.get_emoji(aoe4_discord.consts.RELIC_EMOJI_ID_IN_EGGS)

    best_kill_score_relic = aoe4_discord.models.RelicRow(
        id=0,  # not used for writing
        game_id=game_id,
        name="Best Kill Score",
        score=round(best_kill_weighted_by_kd),
        winner=bkwkd_player,
        created_at=None  # not used for writing
    )

    best_military_relic = aoe4_discord.models.RelicRow(
        id=0,
        game_id=game_id,
        name="Best Military",
        score=round(highest_avg_military),
        winner=ham_player,
        created_at=None
    )
    best_economy_relic = aoe4_discord.models.RelicRow(
        id=0,
        game_id=game_id,
        name="Best Economy",
        score=round(highest_avg_economy),
        winner=hae_player,
        created_at=None
    )

    all_relics = [
        best_kill_score_relic,
        best_military_relic,
        best_economy_relic
    ]

    for relic in all_relics:
        embed.add_field(
            name=relic["name"],
            value=f"{relic_emote} {relic['winner']} ({relic['score']})",
            inline=False
        )

    await ctx.send(embed=embed)

    aoe4_discord.db.write_games(game)

    if game["game_mode"] != "rm_1v1":  # no 1v1s
        aoe4_discord.db.write_relics(*all_relics)

@AOE4DiscordBot.command(name="harmonize", help="Brings all things together")
async def harmonize(ctx: discord.ext.commands.Context) -> None:
    pass

@AOE4DiscordBot.command(name="tally", help="Retrieve the divine tally.")
async def tally(ctx: discord.ext.commands.Context) -> None:
    relic_names = [
        "Best Kill Score",
        "Best Military",
        "Best Economy",
    ]

    relic_stats = [
        aoe4_discord.db.read_relic_stats(relic)
        for relic in relic_names
    ]
    relic_emote = AOE4DiscordBot.get_emoji(aoe4_discord.consts.RELIC_EMOJI_ID_IN_EGGS)
    embed = discord.Embed(
        title=f"{relic_emote} Relic Divine Tally {relic_emote}",
        color=discord.Color.blue()
    )

    for relic_stat in relic_stats:
        embed.add_field(
            name="Relic",
            value=relic_stat["name"],
            inline=False
        )
        embed.add_field(
            name="Most Relics",
            value=f'{relic_stat["most_relics_player"]} ({relic_stat["most_relics"]})',
            inline=False
        )
        embed.add_field(
            name="Highest Score",
            value=f'{relic_stat["max_score_player"]} ({relic_stat["max_score"]})',
            inline=False
        )
        embed.add_field(name=f"{relic_emote}" * 9, value="", inline=False)

    await ctx.send(embed=embed)


@AOE4DiscordBot.command(name="prophecy", help="Get win probability of game")
async def prophecy(
        ctx: discord.ext.commands.Context,
        profile: typing.Optional[aoe4_discord.consts.Idiot] = None,
        game_id: typing.Optional[int] = None,
) -> None:
    """Win probability for a game"""
    if not profile:
        profile = aoe4_discord.consts.Idiot.from_discord_username(ctx.author.name)

    async with aoe4_discord.client.AOE4Client() as client:
        latest_games = await client.get_games(profile)
        if not latest_games:
            await ctx.send("*sings psalm solemnly*")
            return

        latest_game_summaries: tuple[aoe4_discord.models.GameSummary] = await asyncio.gather(*(
            client.get_game_summary(profile, game["game_id"])
            for game in latest_games
        ))

    latest_game_summaries: list[aoe4_discord.models.GameSummary] = [
        game_summary
        for game_summary in latest_game_summaries
        if game_summary
    ]

    if not game_id:
        last_game = latest_games[0]
        game_id = last_game["game_id"]

    game_for_prediction: aoe4_discord.models.Game | None = next((
        game
        for game in latest_games
        if game["game_id"] == game_id
    ), None)

    game_summary_for_prediction: aoe4_discord.models.GameSummary = latest_game_summaries[0]

    if game_summary_for_prediction["gameId"] != game_for_prediction["game_id"]:
        await ctx.send("praying... give me a moment")
        return

    if not game_for_prediction:
        await ctx.send("my mental is blocked")
        return

    player: aoe4_discord.models.PlayerProfile = next((
        player
        for player in game_summary_for_prediction["players"]
        if player["profileId"] == profile.profile_id
    ), None)

    if not player:
        await ctx.send("CRITICAL ERROR")
        return

    result = player["result"]
    civ = player["civilization"]
    team = player["team"]

    latest_game_summaries_with_civ: list[aoe4_discord.models.GameSummary] = [
        game_summary
        for game_summary in latest_game_summaries
        for game_player in game_summary["players"]
        if aoe4_discord.models.is_subdictionary(
            subdict={"profileId": profile.profile_id, "civilization": civ},
            main_dict=game_player,
        )
    ]

    vs_civ_win_rates: dict[str, dict[str, dict[str, int | float]]] = collections.defaultdict(dict)
    ally_civ_win_rates: dict[str, dict[str, dict[str, int | float]]] = collections.defaultdict(dict)

    for latest_game_summary in latest_game_summaries_with_civ:
        for player_profile in latest_game_summary["players"]:

            if player_profile["profileId"] == profile.profile_id:
                player_civ = player_profile["civilization"]
                result = player_profile["result"]  # win or loss

                for game_mate in latest_game_summary["players"]:
                    if game_mate["profileId"] == profile.profile_id:
                        if "self" not in ally_civ_win_rates[player_civ]:
                            ally_civ_win_rates[player_civ]["self"] = {"wins": 0, "games": 0}

                        ally_civ_win_rates[player_civ]["self"]["games"] += 1
                        if result == "win":
                            ally_civ_win_rates[player_civ]["self"]["wins"] += 1
                    elif game_mate["result"] != result:
                        opponent_civ = game_mate["civilization"]

                        if opponent_civ not in vs_civ_win_rates[player_civ]:
                            vs_civ_win_rates[player_civ][opponent_civ] = {"wins": 0, "games": 0}

                        vs_civ_win_rates[player_civ][opponent_civ]["games"] += 1
                        if result == "win":
                            vs_civ_win_rates[player_civ][opponent_civ]["wins"] += 1
                    else:
                        ally_civ = game_mate["civilization"]

                        if ally_civ not in ally_civ_win_rates[player_civ]:
                            ally_civ_win_rates[player_civ][ally_civ] = {"wins": 0, "games": 0}

                        ally_civ_win_rates[player_civ][ally_civ]["games"] += 1
                        if result == "win":
                            ally_civ_win_rates[player_civ][ally_civ]["wins"] += 1

    for player_civ, opponents in vs_civ_win_rates.items():
        for opponent_civ, stats in opponents.items():
            if stats["games"] > 0:
                win_rate = stats["wins"] / stats["games"]
                vs_civ_win_rates[player_civ][opponent_civ]["win_rate"] = round(win_rate, 2)

    for player_civ, opponents in ally_civ_win_rates.items():
        for ally_civ, stats in opponents.items():
            if stats["games"] > 0:
                win_rate = stats["wins"] / stats["games"]
                ally_civ_win_rates[player_civ][ally_civ]["win_rate"] = round(win_rate, 2)

    vs_civs = [
        game_player["civilization"]
        for game_player in game_summary_for_prediction["players"]
        if game_player["team"] != team
    ]

    ally_civs = ["self"] + [
        game_player["civilization"]
        for game_player in game_summary_for_prediction["players"]
        if game_player["team"] == team and game_player["profileId"] != profile.profile_id
    ]

    win_rates_your_team = [
        ally_civ_win_rates.get(civ, {}).get(ally_civ, {}).get("win_rate", -1.0)
        for ally_civ in ally_civs
        if ally_civ_win_rates.get(civ, {}).get(ally_civ, {}).get("win_rate", -1.0) >= 0.0
    ]

    win_rates_opponent_team = [
        1 - vs_civ_win_rates.get(civ, {}).get(vs_civ, {}).get("win_rate", 0.0)
        for vs_civ in vs_civs
        if vs_civ_win_rates.get(civ, {}).get(vs_civ, {}).get("win_rate", -1.0) >= 0.0
    ]

    vs_win_rate = sum(win_rates_opponent_team) / len(win_rates_opponent_team)
    ally_win_rate = sum(win_rates_your_team) / len(win_rates_your_team)

    _ = vs_win_rate / (vs_win_rate + ally_win_rate)
    w_probability = ally_win_rate / (vs_win_rate + ally_win_rate)

    embed = discord.Embed(title="Prophecy", color=discord.Color.blue())
    embed.add_field(
        name="Outcome",
        value=result,
        inline=False,
    )
    embed.add_field(
        name="Ally Civs",
        value=", ".join([civ] + [c for c in ally_civs if c != "self"]),
        inline=False,
    )
    embed.add_field(
        name="Opponent Civs",
        value=", ".join(vs_civs),
        inline=False,
    )
    embed.add_field(
        name="Win Probability",
        value=f"{w_probability*100:.2f}%",
        inline=False,
    )
    await ctx.send(embed=embed)
