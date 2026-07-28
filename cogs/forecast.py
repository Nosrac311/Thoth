import discord
from discord.ext import commands

from config import HITLIST_CHANNELS  # type: ignore
from forecast_embed import build_forecast_embed  # type: ignore
from database import (  # type: ignore
    get_forecast_message,
    save_forecast_message,
)


class Forecast(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channels = {}

    async def update_forecast(self, county):

        # Cache channels
        channel = self.channels.get(county)

        if channel is None:
            channel = self.bot.get_channel(HITLIST_CHANNELS[county])

            if channel is None:
                channel = await self.bot.fetch_channel(
                    HITLIST_CHANNELS[county]
                )

            self.channels[county] = channel

        embed = await build_forecast_embed(county)

        message_id = get_forecast_message(county)

        if message_id:
            try:
                message = await channel.fetch_message(message_id)
                await message.edit(embed=embed)
                return

            except discord.NotFound:
                pass

        # Message doesn't exist anymore
        message = await channel.send(embed=embed)
        save_forecast_message(county, message.id)


async def setup(bot):
    await bot.add_cog(Forecast(bot))
