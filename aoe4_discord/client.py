import typing

import aiohttp
from consts import Idiot
import logging
from models import Game

logger = logging.getLogger(__name__)
_APM_CACHE: dict[str, int] = {}


class AOE4Client:
    """Client for AOE4 World API"""
    def __init__(self, base_url: str = "https://aoe4world.com"):
        """Initialize an aoe4 world api session"""
        self.base_url = base_url
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        self.session = aiohttp.ClientSession()

    async def __aenter__(self) -> 'AOE4Client':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def get_player_profile_and_stats(self, profile: Idiot) -> dict[str, typing.Any] | None:
        """Will retrieve the player profile and stats for a profile by id.
        Endpoint: /v0/players/4635035

        :return:
        """
        endpoint = f"/api/v0/players/{profile.profile_id}"
        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                return None
            data = await response.json()
        return data

    async def get_last_game(self, profile: Idiot) -> dict[str, typing.Any] | None:
        """Will retrieve last games apm for a profile"""
        endpoint = f"/api/v0/players/{profile.profile_id}/games/last"
        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return None
            data = await response.json()
        return data

    async def get_game(self, profile: Idiot, game_id: int) -> dict[str, typing.Any] | None:
        """Get game by ID"""
        endpoint = f"/api/v0/players/{profile.profile_id}/games/{game_id}"
        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return None
            data = await response.json()
        return data

    async def get_game_apm(self, profile: Idiot, game_id: int) -> int | None:
        """Get APM of game by ID"""
        global _APM_CACHE

        endpoint = f"/players/{profile.profile_id}/games/{game_id}/summary?camelize=true"
        cache_key = str(profile.profile_id) + str(game_id)

        if cache_key in _APM_CACHE:
            return _APM_CACHE[cache_key]

        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return None
            data = await response.json()

        player = next(player for player in data["players"] if player["profileId"] == profile.profile_id)
        _APM_CACHE[str(profile.profile_id) + str(game_id)] = player["apm"]

        return player["apm"]

    async def get_games(self, profile: Idiot) -> list[Game] | None:
        """Get most recent games"""
        endpoint = f"/api/v0/players/{profile.profile_id}/games"
        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return
            data = await response.json()

        return data["games"]

    async def get_last_game_with_trophies(self, profile: Idiot) -> Game | None:
        """Retrieve the last game with trophy information for a profile"""
        last_game = await self.get_last_game(profile)
        if not last_game:
            return None

        player_team = None
        for team in last_game["teams"]:
            for player in team:
                if player["profile_id"] == profile.profile_id:
                    player_team = team
                    break
            if player_team:
                break

        if player_team:
            most_kills = {"name": None, "value": 0}
            largest_army = {"name": None, "value": 0}
            most_razed = {"name": None, "value": 0}
            most_economic = {"name": None, "value": 0}

            for player in player_team:
                if player.get("_stats", {}).get("ekills", 0) > most_kills["value"]:
                    most_kills["name"] = player["name"]
                    most_kills["value"] = player["_stats"]["ekills"]
                if player.get("_stats", {}).get("unitprod", 0) > largest_army["value"]:
                    largest_army["name"] = player["name"]
                    largest_army["value"] = player["_stats"]["unitprod"]
                if player.get("_stats", {}).get("structdmg", 0) > most_razed["value"]:
                    most_razed["name"] = player["name"]
                    most_razed["value"] = player["_stats"]["structdmg"]
                if player.get("scores", {}).get("totalcmds", 0) > most_economic["value"]:
                    most_economic["name"] = player["name"]
                    most_economic["value"] = player["scores"]["economy"]

            last_game["trophies"] = {
                "most_kills": f"🏆 {most_kills['name']} ({most_kills['value']})",
                "largest_army": f"🏆 {largest_army['name']} ({largest_army['value']})",
                "most_razed": f"🏆 {most_razed['name']} ({most_razed['value']})",
                "most_economic": f"🏆 {most_economic['name']} ({most_economic['value']})"
            }

        return last_game
