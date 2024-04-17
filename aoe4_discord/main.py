import aoe4_discord
import os
import asyncio


async def main():
    bot = aoe4_discord.AOE4DiscordBot
    await bot.start(token=os.environ["DISCORD_BOT_TOKEN"])


if __name__ == '__main__':
    asyncio.run(main())
