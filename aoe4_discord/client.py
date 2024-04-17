import aiohttp


class AOE4Client:
    """Client for AOE4 World API"""
    def __init__(self, base_url: str = "https://aoe4world.com/api"):
        """Initialize an aoe4 world api session"""
        self.base_url = base_url
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        self.session = aiohttp.ClientSession()

    async def __aenter__(self) -> 'AOE4Client':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def get_player_profile_and_stats(self, profile_id: int) -> None:
        """Will retrieve the player profile and stats for a profile by id.
        Endpoint: /v0/players/4635035

        :return:
        """
        endpoint = f"/v0/players/{profile_id}"
        async with self.session.get(self.base_url + endpoint) as response:
            if response.status != 200:
                return None
            data = await response.json()
        return data
