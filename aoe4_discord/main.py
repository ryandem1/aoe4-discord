import aoe4_discord.bot
import os
import asyncio


async def main():
    bot = aoe4_discord.bot.AOE4DiscordBot
    await bot.start(token=os.environ["DISCORD_BOT_TOKEN"])


if __name__ == '__main__':
    asyncio.run(main())
