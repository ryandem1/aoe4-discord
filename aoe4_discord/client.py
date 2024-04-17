import typing

import aiohttp
from consts import Idiot
import logging

logger = logging.getLogger(__name__)


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

    async def get_last_game_id(self, profile: Idiot) -> int | None:
        """Will retrieve last games apm for a profile"""
        endpoint = f"/api/v0/players/{profile.profile_id}/games/last"
        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return None
            data = await response.json()
        return data["game_id"]

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
        endpoint = f"/players/{profile.profile_id}/games/{game_id}/summary?camelize=true"
        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                logger.error(f"Error from API. Response Status: {response.status}. Text: {response.json()}")
                return None
            data = await response.json()

        player = next(player for player in data["players"] if player["profileId"] == profile.profile_id)
        return player["apm"]
