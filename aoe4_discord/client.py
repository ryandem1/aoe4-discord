import typing

import aiohttp
import logging
import aoe4_discord
import aoe4_discord.consts
import aoe4_discord.models

logger = logging.getLogger(__name__)
_APM_CACHE: dict[str, int] = {}
_GAME_SUMMARY_CACHE: dict[str, dict[str, typing.Any]] = {}


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

    async def get_player_profile_and_stats(self, profile: aoe4_discord.consts.Idiot) -> dict[str, typing.Any] | None:
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

    async def get_last_game(self, profile: aoe4_discord.consts.Idiot) -> aoe4_discord.models.Game | None:
        """Will retrieve last games apm for a profile"""
        endpoint = f"/api/v0/players/{profile.profile_id}/games"
        async with self.session.get(self.base_url + endpoint, params={"limit": 1}) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return None
            data = await response.json()

        if not data["games"]:
            return
        return data["games"][0]

    async def get_game(self, profile: aoe4_discord.consts.Idiot, game_id: int) -> dict[str, typing.Any] | None:
        """Get game by ID"""
        endpoint = f"/api/v0/players/{profile.profile_id}/games/{game_id}"
        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return None
            data = await response.json()
        return data

    async def get_game_apm(self, profile: aoe4_discord.consts.Idiot, game_id: int) -> int | None:
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

    async def get_games(self, profile: aoe4_discord.consts.Idiot) -> list[aoe4_discord.models.Game] | None:
        """Get most recent games"""
        endpoint = f"/api/v0/players/{profile.profile_id}/games"
        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return
            data = await response.json()

        return data["games"]

    async def get_game_summary(
            self,
            profile: aoe4_discord.consts.Idiot,
            game_id: int
    ) -> aoe4_discord.models.GameSummary | None:
        """Get game summary by ID"""
        endpoint = f"/players/{profile.profile_id}/games/{game_id}/summary"
        cache_key = str(profile.profile_id) + str(game_id)

        if cache_key in _GAME_SUMMARY_CACHE:
            return _GAME_SUMMARY_CACHE[cache_key]

        async with self.session.get(self.base_url + endpoint, params={"camelize": "true"}) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return None
            data = await response.json()

        data = aoe4_discord.models.filter_dict_to_type(data, aoe4_discord.models.GameSummary)
        _GAME_SUMMARY_CACHE[cache_key] = data
        return data
